import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import MainPage from './page/MainPage/MainPage.js';
function App() {
    return (
        <>
            <Router>
                <Routes>
                    <Route path='/' element={<MainPage />} />
                </Routes>
            </Router>
        </>
    );
}

export default App;
