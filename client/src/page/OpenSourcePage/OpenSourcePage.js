import Header from "../../component/Header/Header.js";
import ShortButton from "../../component/ShortButton/ShortButton.js";
import { OpenSourceContainer, OpenSourceContent } from "./OpenSourcePage.style.js";
import { useNavigate } from "react-router-dom";

function OpenSourcePage() {
    const navigate = useNavigate();
    const GoBackButtonClick = () => {
        navigate(-1);
    };

    return (
        <>
            <OpenSourceContainer>
                <Header />
                <OpenSourceContent>이후 내용 추가 할 예정</OpenSourceContent>
                <ShortButton txt="뒤로가기" onClick={GoBackButtonClick} />
            </OpenSourceContainer>
        </>
    );
}

export default OpenSourcePage;
