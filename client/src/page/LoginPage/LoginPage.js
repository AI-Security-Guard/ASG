import React, { useState } from "react";
import * as S from "./LoginPage.style";
import Header from "../../component/Header/Header.js";
import LongButton from "../../component/LongButton/LongButton.js";
import Input from "../../component/Input/Input.js";
function LoginPage() {
    const [id, setId] = useState("");
    const [password, setPassword] = useState("");
    const [showModal, setShowModal] = useState(false);

    const handleLogin = () => {
        if (!id || !password) {
            setShowModal(true);
            return;
        }

        console.log("로그인 시도:", { id, password });
    };
    return (
        <>
            <Header />
            <S.Container>
                <S.LoginBox>
                    <S.Title>로그인</S.Title>
                    <Input label="아이디" variant="outlined" value={id} onChange={(e) => setId(e.target.value)} />
                    <Input
                        label="비밀번호"
                        variant="outlined"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                    <LongButton txt="로그인" onClick={handleLogin} />
                </S.LoginBox>
            </S.Container>
        </>
    );
}

export default LoginPage;
