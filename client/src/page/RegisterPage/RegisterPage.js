import React, { useState } from "react";
import Header from "../../component/Header/Header";
import * as S from "./RegisterPage.style";
import Input from "../../component/Input/Input.js";
import LongButton from "../../component/LongButton/LongButton.js";
import { useNavigate } from "react-router-dom";

function RegisterPage() {
    const [id, setId] = useState("");
    const [password, setPassword] = useState("");
    const [passwordCheck, setPasswordCheck] = useState("");
    const navigate = useNavigate();
    const handleRegister = () => {
        console.log("회원가입 시도:", { id, password, password });
        navigate("/termspage");
    };

    return (
        <>
            <Header />
            <S.Container>
                <S.RegisterBox>
                    <S.Title>회원가입</S.Title>
                    <Input
                        label="아이디"
                        value={id}
                        onChange={(e) => setId(e.target.value)}
                        helperText={id.length > 0 && id.length < 4 ? "아이디는 최소 4자 이상이어야 합니다." : " "}
                        variant="outlined"
                    />
                    <Input
                        label="비밀번호"
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        helperText={
                            password.length > 0 && password.length < 6 ? "비밀번호는 최소 6자 이상이어야 합니다." : " "
                        }
                    />
                    <Input
                        label="비밀번호 확인"
                        type="password"
                        value={passwordCheck}
                        onChange={(e) => setPasswordCheck(e.target.value)}
                        helperText={
                            password && passwordCheck && password !== passwordCheck
                                ? "비밀번호가 일치하지 않습니다."
                                : " "
                        }
                    />
                    <LongButton txt="가입하기" onClick={handleRegister} />
                </S.RegisterBox>
            </S.Container>
        </>
    );
}

export default RegisterPage;
