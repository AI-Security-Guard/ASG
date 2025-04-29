import styled, { keyframes } from 'styled-components';

const roll = keyframes`
  0% {
    transform: translateX(-200%) rotate(0deg);
  }
  100% {
    transform: translateX(0) rotate(360deg);
  }
`;

const fadeIn = keyframes`
  0% {
    opacity: 0;
  }
  100% {
    opacity: 1;
  }
`;

export const MainContainer = styled.div`
    height: 100vh;
`;

export const Logo = styled.div`
    flex-direction: column;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
`;

export const LogoImg = styled.img`
    width: 20em;
    animation: ${roll} 1s ease-out;
`;

export const LogoTxt = styled.div`
    font-size: 3rem;
    font-weight: bold;
    opacity: 0;
    animation: ${fadeIn} 1s ease-out forwards;
    animation-delay: 1s;
`;
