import { MainContainer, Logo, LogoImg, LogoTxt } from './MainPage.style.js';
import Header from '../../component/Header/Header.js';
import Sidebar from '../../component/Sidebar/Sidebar.js';
function MainPage() {
    return (
        <>
            <Header />
            <MainContainer>
                <Logo>
                    <LogoImg src='/image/cctv.png' alt='로고 이미지' />
                    <LogoTxt>AI방범대</LogoTxt>
                </Logo>
            </MainContainer>
        </>
    );
}

export default MainPage;
