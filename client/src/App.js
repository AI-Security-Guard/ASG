import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import MainPage from './page/MainPage/MainPage.js';
import ListPage from './page/ListPage/ListPage.js';

function App() {
    return (
        <>
            <Router>
                <Routes>
                    <Route path='/' element={<MainPage />} />
                    <Route path='/List' element={<ListPage />} />
                </Routes>
            </Router>
        </>
    );
}

export default App;
