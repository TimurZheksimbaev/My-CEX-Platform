import { useState, useEffect } from 'react';
import axiosInstance from '../utils/axiosInstance';
import '../styles/WalletModal.css';

const WalletModal = ({ isOpen, onClose }) => {
  const [walletInfo, setWalletInfo] = useState([]);
  const [depositAmount, setDepositAmount] = useState('');
  const [depositSymbol, setDepositSymbol] = useState('');
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Fetch wallet info
  const fetchWalletInfo = async () => {
    try {
      const response = await axiosInstance.get('/wallet/balance');
      setWalletInfo(response.data);
    } catch (err) {
      setError('Failed to fetch wallet information.');
    }
  };

  // Create a new wallet
  const handleCreateWallet = async () => {
    try {
      await axiosInstance.post('/wallet/create');
      setSuccessMessage('Wallet created successfully!');
      fetchWalletInfo(); // Refresh wallet info
    } catch (err) {
      setError('Failed to create wallet.');
    }
  };

  // Deposit to wallet
  const handleDeposit = async () => {
    if (!depositSymbol || parseFloat(depositAmount) <= 0) {
      setError('Please provide a valid deposit symbol and amount.');
      return;
    }

    try {
      await axiosInstance.post('/wallet/deposit', {
        crypto_symbol: depositSymbol,
        amount: parseFloat(depositAmount),
      });
      setSuccessMessage(`Deposited ${depositAmount} ${depositSymbol} successfully!`);
      setDepositAmount('');
      setDepositSymbol('');
      fetchWalletInfo(); // Refresh wallet info
    } catch (err) {
      setError('Failed to deposit funds.');
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchWalletInfo();
    }
  }, [isOpen]);

  if (!isOpen) {
    return null;
  }

  return (
    <div className="modal-overlay">
      <div className="modal">
        <h2>Wallet Info</h2>
        {error && <p className="error-message">{error}</p>}
        {successMessage && <p className="success-message">{successMessage}</p>}

        <table className="wallet-table">
          <thead>
            <tr>
              <th>Currency</th>
              <th>Balance</th>
            </tr>
          </thead>
          <tbody>
            {walletInfo.length > 0 ? (
              walletInfo.map((wallet) => (
                <tr key={wallet.crypto_symbol}>
                  <td>{wallet.crypto_symbol}</td>
                  <td>{wallet.balance}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan="2">No wallet data available.</td>
              </tr>
            )}
          </tbody>
        </table>
        <button className="submit-button" onClick={handleCreateWallet}>
          Create Wallet
        </button>
        <div className="deposit-form">
          <h3>Deposit Funds</h3>
          <input
            type="text"
            placeholder="Currency (e.g., BTC)"
            value={depositSymbol}
            onChange={(e) => setDepositSymbol(e.target.value)}
          />
          <input
            type="number"
            placeholder="Amount"
            value={depositAmount}
            onChange={(e) => setDepositAmount(e.target.value)}
          />
          <button className="submit-button" onClick={handleDeposit}>
            Deposit
          </button>
        </div>
        <button className="close-button" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
};

export default WalletModal;
