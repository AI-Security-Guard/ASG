import React, { useState } from 'react';
import * as S from './LoginPage.style';
import Header from '../../component/Header/Header.js'
function LoginPage() {
  const [id, setId] = useState('');
  const [password, setPassword] = useState('');
  const [showModal, setShowModal] = useState(false);

  const handleLogin=()=>{
    if(!id||!password){
      setShowModal(true);
      return;
    }

    console.log('로그인 시도:',{id,password});
  };
  return (
    <>
      <Header />
      <S.Container>
        <S.LoginBox>
          <S.Title>로그인</S.Title>

          <S.Label>아이디</S.Label>
          <S.Input 
          type="id" 
          placeholder=""
          value={id}
          onChange={(e)=>setId(e.target.value)}
          />

          <S.Label>비밀번호</S.Label>
          <S.Input 
          type="password" 
          placeholder=""
          value={password}
          onChange={(e)=>setPassword(e.target.value)} 
          />

          <S.Button onClick={handleLogin}>로그인</S.Button>

          
        </S.LoginBox>
      </S.Container>
    </>
  );
}

export default LoginPage;
