import React, { useEffect, useState } from 'react';
import client from '../api/client';
import Navbar from '../components/Navbar';

const HomeView = () => {
  const [products, setProducts] = useState([]);

  useEffect(() => {
    client.get('/api/products/')
      .then(res => setProducts(res.data.results || res.data))
      .catch(err => console.error(err));
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-8">Pharmacy Catalog</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {products.map(product => (
          <div key={product.id} className="border p-4 rounded shadow hover:shadow-lg transition-shadow">
            <h2 className="text-xl font-semibold mb-2">{product.name}</h2>
            <p className="text-gray-600 mb-4">{product.summary}</p>
            <div className="flex justify-between items-center">
              <span className="text-blue-600 font-bold">{product.price} DA</span>
              <button className="bg-green-500 text-white px-4 py-2 rounded">Add to Cart</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default HomeView;
