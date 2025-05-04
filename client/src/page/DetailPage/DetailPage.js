import * as D from './Detail.style.js';
import Header from '../../component/Header/Header.js';
import ShortButton from '../../component/ShortButton/ShortButton.js';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function DetailPage() {
    const navigate = useNavigate();

    //useState 초기값은 이후 수정 필요
    const [video, setVideo] = useState('/video.mp4');
    const [date, setDate] = useState('2025/04/28/23:00:00');
    const [type, setType] = useState('살인');
    const [coordinate, setCoordinate] = useState('(123,123231)');

    const GoBackButtonClick = () => {
        navigate(-1);
    };

    return (
        <>
            <Header />
            <D.DetailContainer>
                <D.Detail>
                    <D.TempVideo controls>
                        <source src={video} type='video/mp4' />
                    </D.TempVideo>
                    <D.DetailContent>
                        <D.Date>발생시기: {date}</D.Date>
                        <D.Type>수상행동 유형: {type}</D.Type>
                        <D.Location>최초 발생 위치: {coordinate}</D.Location>
                    </D.DetailContent>
                </D.Detail>
                <D.ButtonContainer>
                    <ShortButton txt='뒤로가기' onClick={GoBackButtonClick} />
                </D.ButtonContainer>
            </D.DetailContainer>
        </>
    );
}

export default DetailPage;
