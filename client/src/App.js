import './App.css';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import MainPage from './page/MainPage/MainPage.js';
<<<<<<< Updated upstream
import ListPage from './page/ListPage/ListPage.js';
import DetailPage from './page/DetailPage/DetailPage.js';

=======
import LoginPage from './page/LoginPage/LoginPage.js';
import RegisterPage from './page/RegisterPage/RegisterPage.js';
import RenderPage from './page/RenderPage/RenderPage.js';
>>>>>>> Stashed changes
function App() {
    return (
        <>
            <Router>
                <Routes>
                    <Route path='/' element={<MainPage />} />
<<<<<<< Updated upstream
                    <Route path='/List' element={<ListPage />} />
                    <Route path='/Detail' element={<DetailPage />} />
=======
                    <Route path='/login' element={<LoginPage />} />
                    <Route path='/register' element={<RegisterPage />} />
                    <Route path='/render' element={<RenderPage />} />
>>>>>>> Stashed changes
                </Routes>
            </Router>
        </>
    );
}

export default App;
