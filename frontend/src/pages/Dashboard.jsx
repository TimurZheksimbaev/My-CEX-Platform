import { useEffect, useState } from 'react';
import axiosInstance from '../utils/axiosInstance';
import WalletModal from '../components/WalletModal';
import '../styles/Dashboard.css';

const Dashboard = () => {
  const [orders, setOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null); // Selected order for execution
  const [executeAmount, setExecuteAmount] = useState('');
  const [isWalletModalOpen, setIsWalletModalOpen] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');
  const [isCreateOrderModalOpen, setIsCreateOrderModalOpen] = useState(false); // Control create order modal
  const [newOrder, setNewOrder] = useState({
    
    type: 'buy',
    trading_pair: '',
    amount: '',
  });

  // Fetch orders from order book
  const fetchOrders = async () => {
    try {
      const response = await axiosInstance.get('/order/order_book');
      setOrders(response.data);
    } catch (err) {
      setError('Failed to fetch orders.');
    }
  };

  // Create a new order
  const handleCreateOrder = async (e) => {
    e.preventDefault();
    if (!newOrder.trading_pair || !newOrder.amount || parseFloat(newOrder.amount) <= 0) {
      setError('Please fill all fields with valid values.');
      return;
    }

    try {
      await axiosInstance.post('/order/', {
        type: newOrder.type,
        trading_pair: newOrder.trading_pair,
        amount: parseFloat(newOrder.amount),
      });
      setSuccessMessage('Order created successfully!');
      setNewOrder({ type: 'buy', trading_pair: '', amount: '' });
      setIsCreateOrderModalOpen(false); // Close modal
      fetchOrders(); // Refresh orders list
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create order.');
    }
  };

  // Execute an existing order
  const handleExecuteOrder = async () => {
    if (!executeAmount || parseFloat(executeAmount) <= 0) {
      setError('Please enter a valid amount.');
      return;
    }

    try {
      console.log(selectedOrder.order.id)
      console.log(executeAmount)
      await axiosInstance.post('/order/execute/', {
        order_id: selectedOrder.order.id,
        amount: parseFloat(executeAmount),
      });
      setSuccessMessage(`Order ${selectedOrder.order.id} executed successfully!`);
      setSelectedOrder(null); // Close execution modal
      fetchOrders(); // Refresh orders list
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to execute order.');
    }
  };

  // useEffect(() => {
  //   fetchOrders();
  // }, []);

  useEffect(() => {
    fetchOrders(); // Fetch data initially
    const interval = setInterval(() => {
      fetchOrders();
    }, 3000);

    return () => clearInterval(interval); // Cleanup interval on component unmount
  }, []);
  return ( 
    <>
      <header>
        <button className="wallet-button" onClick={() => setIsWalletModalOpen(true)}>
          Wallet
        </button>
      </header>
      <div className="dashboard-container">
      <h1>Orders</h1>
      {error && <p className="error-message">{error}</p>}
      {successMessage && <p className="success-message">{successMessage}</p>}

      {/* Create Order Button */}
      <button className="create-order-button" onClick={() => setIsCreateOrderModalOpen(true)}>
        Create Order
      </button>

      {/* Orders Table */}
      {orders.length > 0 ? (
        <table className="orders-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>User</th>
              <th>Type</th>
              <th>Trading Pair</th>
              <th>Price</th>
              <th>Amount</th>
              <th>Created At</th>
            </tr>
          </thead>
          <tbody>
            {orders.map((order) => (
              <tr
                key={order.id}
                onClick={() => {
                  setSelectedOrder(order); // Open execution modal
                  setExecuteAmount(''); // Reset the input field
                  setError(''); // Clear any previous errors
                }}
              >
                <td>{order.order.id}</td>
                <td>{order.email}</td>
                <td className={order.order.type === 'sell' ? 'sell' : 'buy'}>{order.order.type}</td>
                <td>{order.order.trading_pair}</td>
                <td>{order.order.price ? order.order.price : '-'}</td>
                <td>{order.order.amount}</td>
                <td>{new Date(order.order.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p className="no-orders">No orders available.</p>
      )}

      {/* Create Order Modal */}

      {/* Модальное окно для создания ордера */}
      {isCreateOrderModalOpen && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Create Order</h2>
            <form onSubmit={handleCreateOrder}>
              <div>
                <label>Type:</label>
                <select
                  value={newOrder.type}
                  onChange={(e) => setNewOrder({ ...newOrder, type: e.target.value })}
                >
                  <option value="buy">Buy</option>
                  <option value="sell">Sell</option>
                </select>
              </div>
              <div>
                <label>Trading Pair:</label>
                <input
                  type="text"
                  placeholder="e.g., BTC-USDT"
                  value={newOrder.trading_pair}
                  onChange={(e) => setNewOrder({ ...newOrder, trading_pair: e.target.value })}
                  required
                />
              </div>
              <div>
                <label>Amount:</label>
                <input
                  type="number"
                  placeholder="Enter amount"
                  value={newOrder.amount}
                  onChange={(e) => setNewOrder({ ...newOrder, amount: e.target.value })}
                  required
                />
              </div>
              <button type="submit" className="submit-button">
                Create Order
              </button>
              <button
                type="button"
                className="close-button"
                onClick={() => setIsCreateOrderModalOpen(false)}
              >
                Close
              </button>
            </form>
          </div>
        </div>
      )}


     {/* Модальное окно выполнения ордера */}
     {selectedOrder && (
        <div className="modal-overlay">
          <div className="modal">
            <h2>Execute Order</h2>
            <p>
              <strong>Order ID:</strong> {selectedOrder.order.id}
            </p>
            <p>
              <strong>Type:</strong> {selectedOrder.order.type}
            </p>
            <p>
              <strong>Trading Pair:</strong> {selectedOrder.order.trading_pair}
            </p>
            <p>
              <strong>Price:</strong> {selectedOrder.order.price ? selectedOrder.order.price : '-'}
            </p>
            <p>
              <strong>Available Amount:</strong> {selectedOrder.order.amount}
            </p>
            <input
              type="number"
              placeholder="Enter amount to execute"
              value={executeAmount}
              onChange={(e) => setExecuteAmount(e.target.value)}
              className="modal-input"
              required
            />
            <button className="execute-button" onClick={handleExecuteOrder}>
              Execute Order
            </button>
            <button className="close-button" onClick={() => setSelectedOrder(null)}>
              Close
            </button>
          </div>
        </div>
      )}

      {/* Wallet Modal */}
      <WalletModal isOpen={isWalletModalOpen} onClose={() => setIsWalletModalOpen(false)} />
    </div>
  </>);
};

export default Dashboard;
