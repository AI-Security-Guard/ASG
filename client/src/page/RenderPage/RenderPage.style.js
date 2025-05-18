import styled from 'styled-components';

export const MainLayout = styled.div`
  display: flex;
  height: calc(100vh - 80px); /* 헤더 제외 전체 높이 */
`;

export const ContentArea = styled.div`
  width: 84%;               
  margin-left: auto;        
  background-color: white;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  position: relative;
`;

export const PlusIcon = styled.div`
  position: absolute;
  top: 60%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 60px;
  color: #bbb;
  opacity: 0.6;
  cursor: pointer;
`;

