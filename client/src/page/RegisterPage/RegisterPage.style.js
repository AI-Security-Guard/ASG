import styled from 'styled-components';

export const Container = styled.div`
  position: relative;
  width: 100%;
  height: 100vh;
`;

export const RegisterBox = styled.div`
  position: absolute;
  top: 150px;
  left: 50%;
  transform: translateX(-50%);
  background-color: #aaa;
  padding: 40px;
  border-radius: 10px;
  width: 400px;
`;

export const Title = styled.h2`
  text-align: center;
  font-family: 'Gowun Dodum', sans-serif;
`;

export const Label = styled.label`
  display: block;
  margin-top: 15px;
  font-weight: bold;
`;

export const Input = styled.input`
  width: 95%;
  padding: 10px;
  margin-top: 5px;
  border-radius: 5px;
  border: none;
  background-color: #ddd;
`;

export const Error = styled.p`
  color: red;
  font-size: 13px;
  margin: 5px 0 0 0;
`;

export const Button = styled.button`
  margin-top: 30px;
  width: 100%;
  padding: 15px;
  border: none;
  border-radius: 30px;
  background-color: black;
  color: white;
  font-weight: bold;
  font-size: 16px;
  cursor: pointer;
`;
