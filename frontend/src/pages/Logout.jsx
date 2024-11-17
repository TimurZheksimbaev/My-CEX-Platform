import Login from "./Login";

export default function Logout() {
    localStorage.removeItem('token'); // Clear token from localStorage
    return <Login />
}

