import json
import logging
import os
import sys
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pika

logging.basicConfig(level=logging.INFO, format="%(asctime)s [worker] %(message)s")
logger = logging.getLogger(__name__)

AMQP_URL = os.environ.get("AMQP_URL", "amqp://guest:guest@rabbitmq:5672/")
EXCHANGE = "marketpharm"
QUEUE = "notifications"
ROUTING_KEY = "order.created"

SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")

def send_email(to_address, subject, html_content):
    if not SMTP_USER or not SMTP_PASS:
        logger.error("Détails SMTP manquants. L'e-mail ne peut pas être envoyé.")
        return False
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_USER
        msg['To'] = to_address
        msg['Subject'] = subject

        msg.attach(MIMEText(html_content, 'html'))
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'e-mail : {e}")
        return False


def main():
    while True:
        try:
            params = pika.URLParameters(AMQP_URL)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
            channel.queue_declare(queue=QUEUE, durable=True)
            channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key="order.created")
            channel.queue_bind(exchange=EXCHANGE, queue=QUEUE, routing_key="stock.empty")
            logger.info("En écoute sur %s (order.created & stock.empty)", QUEUE)

            def callback(ch, method, properties, body):
                try:
                    payload = json.loads(body.decode("utf-8"))
                except json.JSONDecodeError:
                    payload = {"raw": body.decode("utf-8", errors="replace")}
                
                if method.routing_key == "order.created":
                    logger.info("Notification commande reçue : %s", payload)
                    order_id = payload.get("order_id")
                    email = payload.get("email")
                    if email:
                        logger.info(f"Envoi de l'e-mail de confirmation à {email}...")
                        html_content = f"""
                        <html>
                          <body>
                            <h2 style="color: #10b981;">Confirmation de votre commande!</h2>
                            <p>Bonjour,</p>
                            <p>Votre commande <strong>#{order_id}</strong> a été enregistrée avec succès sur MarketPharm.</p>
                            <p>Nous vous remercions pour votre confiance et nous préparons votre expédition.</p>
                            <br/>
                            <p>L'équipe MarketPharm</p>
                          </body>
                        </html>
                        """
                        success = send_email(email, f"Votre commande #{order_id} - MarketPharm", html_content)
                        if success:
                            logger.info(f"E-mail envoyé avec succès à {email}")
                    else:
                        logger.warning("Aucun e-mail fourni dans la commande, pas d'e-mail envoyé.")
                elif method.routing_key == "stock.empty":
                    logger.warning("ALERTE STOCK — Produit '%s' (ID:%s) est en rupture !", 
                                   payload.get("product_name"), payload.get("product_id"))
                else:
                    logger.info("Notification reçue [%s]: %s", method.routing_key, payload)
                
                ch.basic_ack(delivery_tag=method.delivery_tag)

            channel.basic_qos(prefetch_count=10)
            channel.basic_consume(queue=QUEUE, on_message_callback=callback)
            channel.start_consuming()
        except (pika.exceptions.AMQPConnectionError, OSError) as e:
            logger.warning("Connexion RabbitMQ indisponible (%s), nouvel essai dans 3s…", e)
            time.sleep(3)
        except KeyboardInterrupt:
            sys.exit(0)


if __name__ == "__main__":
    main()
