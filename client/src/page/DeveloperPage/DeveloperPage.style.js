import styled, { keyframes } from "styled-components";

const gradientShift = keyframes`
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
`;

export const DeveloperContainer = styled.div`
    display: flex;
    width: 100%;
    height: 100%;
    position: absolute;
    align-items: center;
    justify-content: center;

    background: linear-gradient(135deg, #e5e7eb, #cbd5e1, #94a3b8, #cbd5e1);
    background-size: 300% 300%;
    animation: ${gradientShift} 20s ease-in-out infinite;
`;
