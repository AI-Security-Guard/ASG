import "./App.css";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Background from "./component/Background/Background.js";
import MainPage from "./page/MainPage/MainPage.js";
import ListPage from "./page/ListPage/ListPage.js";
import DetailPage from "./page/DetailPage/DetailPage.js";
import RegisterPage from "./page/RegisterPage/RegisterPage.js";
import DeveloperPage from "./page/DeveloperPage/DeveloperPage.js";
import LoginPage from './page/LoginPage/LoginPage.js';
import RenderPage from './page/RenderPage/RenderPage';

function App() {
    return (
        <>
            <Router>
                <Background>
                    <Routes>
                       <Route path='/login' element={<LoginPage />} />
                        <Route path="/" element={<MainPage />} />
                        <Route path="/List" element={<ListPage />} />
                        <Route path="/Detail" element={<DetailPage />} />
                        <Route path="/register" element={<RegisterPage />} />
                           <Route path="/render" element={<RenderPage />} />
                    </Routes>
                </Background>
            </Router>
        </>
    );
}

export default App;
