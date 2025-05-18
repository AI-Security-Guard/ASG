import React from 'react';
import * as S from './RenderPage.style';
import Header from '../../component/Header/Header';
import Sidebar from '../../component/Sidebar/Sidebar';

function RenderPage() {
  return (
    <>
      <Header />
      <S.MainLayout>
        <Sidebar />
        <S.ContentArea>
          <S.PlusIcon>＋</S.PlusIcon>
        </S.ContentArea>
      </S.MainLayout>
    </>
  );
}

export default RenderPage;
