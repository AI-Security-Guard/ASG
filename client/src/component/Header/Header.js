import React, { useState } from "react";
import {
    HeaderContainer,
    Logo,
    LogoImg,
    LogoTxt,
    UserAuthBox,
    LoginButton,
    RegisterButton,
    WelcomeMessage,
    Logout,
} from "./Header.style.js";

function Header() {
    const [isLogin, setIsLogin] = useState(false);
    const [id, setId] = useState("sojeong0302");

    return (
        <>
            <HeaderContainer>
                <Logo>
                    <LogoImg src="/image/logo.png" alt="로고 이미지" />
                    <LogoTxt>AI방범대</LogoTxt>
                </Logo>
                <UserAuthBox>
                    {isLogin ? (
                        <>
                            <WelcomeMessage>{id}님 환영합니다!</WelcomeMessage>
                            <Logout>로그아웃</Logout>
                        </>
                    ) : (
                        <>
                            <LoginButton>로그인</LoginButton>
                            <RegisterButton>회원가입</RegisterButton>
                        </>
                    )}
                </UserAuthBox>
            </HeaderContainer>
        </>
    );
}

export default Header;
