import styled from 'styled-components';

export const HeaderContainer = styled.div`
    background: linear-gradient(to right, #cdcecf 0%, #272727 100%);
    height: 50%;
    display: flex;
    justify-content: space-between;
    padding: 1%;
`;

export const Logo = styled.div`
    display: flex;
    align-items: center;
`;

export const LogoImg = styled.img`
    width: 80px;
    cursor: pointer;
`;

export const LogoTxt = styled.div`
    font-size: 1.2rem;
    font-weight: bold;
`;

export const UserAuthBox = styled.div`
    display: flex;
    gap: 10%;
    align-items: center;
    width: 8em;
`;

export const LoginButton = styled.div`
    color: white;
    cursor: pointer;
`;

export const RegisterButton = styled.div`
    color: white;
    cursor: pointer;
`;
