import "./App.css";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Background from "./component/Background/Background.js";
import MainPage from "./page/MainPage/MainPage.js";
import ListPage from "./page/ListPage/ListPage.js";
import DetailPage from "./page/DetailPage/DetailPage.js";
import TermsPage from "./page/TermsPage/TermsPage.js";

function App() {
    return (
        <>
            <Router>
                <Background>
                    <Routes>
                        <Route path="/" element={<MainPage />} />
                        <Route path="/List" element={<ListPage />} />
                        <Route path="/Detail" element={<DetailPage />} />
                        <Route path="/termspage" element={<TermsPage />} />
                    </Routes>
                </Background>
            </Router>
        </>
    );
}

export default App;
