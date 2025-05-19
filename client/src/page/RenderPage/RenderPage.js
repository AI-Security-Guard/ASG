import React from "react";
import * as S from "./RenderPage.style";
import Header from "../../component/Header/Header";
import Sidebar from "../../component/Sidebar/Sidebar";

function RenderPage() {
    return (
        <>
            <S.MainLayout>
                <Header />
                <Sidebar />
                <S.ContentArea>
                    <S.PlusIcon src="/image/addToVideo.png" alt="영상 추가" />
                </S.ContentArea>
            </S.MainLayout>
        </>
    );
}

export default RenderPage;
