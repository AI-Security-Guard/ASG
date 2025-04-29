import { HeaderContainer, Logo, LogoImg, LogoTxt, UserAuthBox, LoginButton, RegisterButton } from './Header.style.js';

function Header() {
    return (
        <>
            <HeaderContainer>
                <Logo>
                    <LogoImg src='/image/logo.png' alt='로고 이미지' />
                    <LogoTxt>AI방범대</LogoTxt>
                </Logo>
                <UserAuthBox>
                    <LoginButton>로그인</LoginButton>
                    <RegisterButton>회원가입</RegisterButton>
                </UserAuthBox>
            </HeaderContainer>
        </>
    );
}

export default Header;
