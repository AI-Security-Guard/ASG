// src/page/LoginPage/LoginPage.style.js
import styled from 'styled-components';

export const Container = styled.div`
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
`;

export const LoginBox = styled.div`
  width: 300px;
  background-color: #B3B3B3;  /* 연한 회색 배경 */
  padding: 40px;
  border-radius: 10px;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
`;

export const Title = styled.h2`
  font-size: 24px;
  text-align: center;
  margin-bottom: 30px;
  font-family: 'Arial', sans-serif;
`;

export const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  margin-top: 16px;
  font-weight: bold;
`;

export const Input = styled.input`
  width: 90%;
  padding: 12px;
  background-color: #dddddd;
  border: none;
  border-radius: 8px;
  font-size: 14px;
`;

export const Button = styled.button`
  width: 100%;
  margin-top: 24px;
  padding: 14px;
  background-color: black;
  color: white;
  font-weight: bold;
  border: none;
  border-radius: 999px;
  font-size: 16px;
  cursor: pointer;

  &:hover {
    background-color: #222;
  }
`;

export const LinkWrapper = styled.div`
  margin-top: 24px;
  text-align: center;
  font-size: 14px;

  a {
    color: #111;
    text-decoration: none;
    margin: 0 6px;
    font-weight: bold;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;




