import styled from 'styled-components';

export const Container = styled.div`
  display: flex;
  justify-content: center;
  padding-top: 100px;
`;

export const Box = styled.div`
  background-color: #aaa;
  padding: 40px;
  border-radius: 10px;
  width: 500px;
  height: auto;
`;

export const Title = styled.h2`
  text-align: center;
  margin-bottom: 20px;
`;

export const SubText = styled.p`
  font-weight: bold;
`;

export const CheckLine = styled.div`
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 20px;
  gap: 227px; 

  input[type='checkbox'] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
`;

export const Section = styled.div`
  background-color: #cbcccd;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 5px;
`;

export const Required = styled.span`
  color: red;
`;

export const TextArea = styled.textarea`
  width: 95%;
  height: 100px;
  resize: none;
  margin: 10px 0;
  padding: 10px;
  font-size: 14px;
`;

export const ButtonGroup = styled.div`
  display: flex;
  justify-content: space-between;
`;

export const BackButton = styled.button`
  background-color: #ccc;
  border: none;
  padding: 10px 20px;
  border-radius: 30px;
  font-size: 16px;
  cursor: pointer;
`;

export const SubmitButton = styled.button`
  background-color: black;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 30px;
  font-size: 16px;
  cursor: pointer;
`;

export const CheckLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: bold;
  font-size: 15px;
  margin-top: 10px;

  input[type='checkbox'] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
`;

export const CheckLabelRow = styled.label`
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;         // 또는 300px, 400px 등 원하는 너비
  font-weight: bold;
  font-size: 16px;

  input[type='checkbox'] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
`;

export const TitleWithCheckbox = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  margin-bottom: 10px;

  input[type='checkbox'] {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
`;