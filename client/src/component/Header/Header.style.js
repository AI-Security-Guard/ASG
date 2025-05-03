import styled from 'styled-components';

export const HeaderContainer = styled.div`
    background: linear-gradient(to right, #cdcecf 0%, #272727 100%);
    position: fixed;
    display: flex;
    height: 10%;
    width: 100%;
    justify-content: space-between;
    border-bottom: 2px solid black;
    z-index: 1;
    top: 0;
`;

export const Logo = styled.div`
    display: flex;
    align-items: center;
    margin-left: 1.2rem;
    cursor: pointer;
`;

export const LogoImg = styled.img`
    width: 70px;
`;

export const LogoTxt = styled.div`
    font-size: 1.2rem;
    font-weight: bold;
`;

export const UserAuthBox = styled.div`
    display: flex;
    gap: 10%;
    align-items: center;
    width: 20em;
    justify-content: flex-end;
    margin-right: 1.2rem;
`;

export const LoginButton = styled.div`
    color: white;
    cursor: pointer;
`;

export const RegisterButton = styled.div`
    color: white;
    cursor: pointer;
`;

export const WelcomeMessage = styled.div`
    color: white;
`;

export const Logout = styled.div`
    color: white;
    cursor: pointer;
`;
