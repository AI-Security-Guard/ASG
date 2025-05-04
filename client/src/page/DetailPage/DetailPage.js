import * as D from './Detail.style.js';
import Header from '../../component/Header/Header.js';
import ShortButton from '../../component/ShortButton/ShortButton.js';

function DetailPage() {
    return (
        <>
            <Header />
            <D.DetailContainer>
                <D.Detail>
                    <D.TempVideo controls>
                        <source src='/video.mp4' type='video/mp4' />
                    </D.TempVideo>
                    <D.DetailContent>
                        <D.Date>발생시기: 2025 / 04 / 28 / 23:00:00</D.Date>
                        <D.Type>수상행동 유형: 폭행</D.Type>
                        <D.Location>최초 발생 위치: (123,123231)</D.Location>
                    </D.DetailContent>
                </D.Detail>
                <D.ButtonContainer>
                    <ShortButton txt='뒤로가기' />
                </D.ButtonContainer>
            </D.DetailContainer>
        </>
    );
}

export default DetailPage;
