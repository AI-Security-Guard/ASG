import { DeveloperContainer } from "./DeveloperPage.style.js";
import Header from "../../component/Header/Header.js";
import Slider from "../../component/Slider/Slider.js";

function DeveloperPage() {
    const slideItems = ["첫 번째 슬라이드", "두 번째 슬라이드", "세 번째 슬라이드"];
    return (
        <>
            <Header />
            <DeveloperContainer>
                <Slider items={slideItems} />
            </DeveloperContainer>
            ;
        </>
    );
}

export default DeveloperPage;
