import styled, { keyframes } from "styled-components";

const gradientShift = keyframes`
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
`;

export const DeveloperContainer = styled.div`
    width: 100%;
    min-height: 100vh;
    background: linear-gradient(135deg, #e5e7eb, #cbd5e1, #94a3b8, #cbd5e1);
    background-size: 300% 300%;
    background-position: 0% 50%;
    animation: ${gradientShift} 20s ease-in-out infinite;

    display: flex;
    justify-content: center;
    align-items: center;
    box-sizing: border-box;
`;

export const SlideBox = styled.div`
    background-color: rgba(248, 250, 252, 0.9);
    width: 100%;
    max-width: 700px;
    margin: 0 auto;
    border-radius: 16px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    justify-content: center;
    display: flex;
    align-items: center;
    flex-direction: column;
`;

export const Tag = styled.span`
    display: inline-block;
    background: #e2e8f0;
    padding: 4px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    margin-left: 6px;
    font-weight: bold;
`;
