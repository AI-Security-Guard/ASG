import React, { useState } from 'react';
import Header from '../../component/Header/Header';
import * as S from './RegisterPage.style';

function RegisterPage() {
  const [id, setId] = useState('');
  const [password, setPassword] = useState('');
  const [passwordCheck, setPasswordCheck] = useState('');
  const [error, setError] = useState('');

  const handleRegister = () => {
    if (id.length < 4) {
      setError('아이디는 최소 4자 이상이어야 합니다.');
      return;
    }
    if (password !== passwordCheck) {
      setError('비밀번호를 확인해주세요');
      return;
    }
    if (password.length < 6) {
      setError('비밀번호는 최소 6자 이상이어야 합니다.');
      return;
    }
    
    setError('');
    console.log('회원가입 시도:', { id, password });
  };

  return (
    <>
      <Header />
      <S.Container>
        <S.RegisterBox>
          <S.Title>회원가입</S.Title>

          <S.Label>아이디</S.Label>
          <S.Input value={id} onChange={(e) => setId(e.target.value)} />

          <S.Label>비밀번호</S.Label>
          <S.Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />

          <S.Label>비밀번호 확인</S.Label>
          <S.Input type="password" value={passwordCheck} onChange={(e) => setPasswordCheck(e.target.value)} />
          {error && <S.Error>{error}</S.Error>}

          <S.Button onClick={handleRegister}>가입하기</S.Button>
        </S.RegisterBox>
      </S.Container>
    </>
  );
}

export default RegisterPage;
