// src/page/LoginPage/LoginPage.style.js
import styled from "styled-components";

export const Container = styled.div`
    width: 100%;
    height: 100vh;
    display: flex;
    justify-content: center;
    align-items: center;
`;

export const LoginBox = styled.div`
    display: flex;
    flex-direction: column;
    justify-content: space-around;
    height: 40%;
    width: 25%;
    background: rgba(255, 255, 255, 0.75);
    padding: 3%;
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.3);
`;

export const Title = styled.h2`
    font-size: 24px;
    text-align: center;
`;

// export const Button = styled.button`
//     width: 100%;
//     margin-top: 24px;
//     padding: 14px;
//     background-color: black;
//     color: white;
//     font-weight: bold;
//     border: none;
//     border-radius: 999px;
//     font-size: 16px;
//     cursor: pointer;

//     &:hover {
//         background-color: #222;
//     }
// `;

// export const LinkWrapper = styled.div`
//     margin-top: 24px;
//     text-align: center;
//     font-size: 14px;

//     a {
//         color: #111;
//         text-decoration: none;
//         margin: 0 6px;
//         font-weight: bold;

//         &:hover {
//             text-decoration: underline;
//         }
//     }
// `;
