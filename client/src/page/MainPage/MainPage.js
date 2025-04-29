import { MainContainer, Logo, LogoImg, LogoTxt } from './MainPage.style.js';

function MainPage() {
    return (
        <>
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
