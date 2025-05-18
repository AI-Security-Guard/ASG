import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import MainPage from './page/MainPage/MainPage.js';
import ListPage from './page/ListPage/ListPage.js';
import DetailPage from './page/DetailPage/DetailPage.js';
import LoginPage from './page/LoginPage/LoginPage.js';
function App() {
    return (
        <>
            <Router>
                <Routes>
                    <Route path='/' element={<MainPage />} />
                    <Route path='/List' element={<ListPage />} />
                    <Route path='/Detail' element={<DetailPage />} />
                    <Route path='/login' element={<LoginPage />} />
                </Routes>
            </Router>
        </>
    );
}

export default App;
