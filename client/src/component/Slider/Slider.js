import React from "react";
import Slider from "react-slick";
import "slick-carousel/slick/slick.css";
import "slick-carousel/slick/slick-theme.css";
import { SliderContainer } from "./Slider.style.js";

function SliderComponent({ items }) {
    const settings = {
        dots: true,
        infinite: true,
        speed: 500,
        slidesToShow: 1,
        slidesToScroll: 1,
        autoplay: true,
        autoplaySpeed: 6000,
    };

    return (
        <SliderContainer>
            <Slider {...settings}>
                {items.map((item, index) => (
                    <div key={index}>{item}</div>
                ))}
            </Slider>
        </SliderContainer>
    );
}

export default SliderComponent;
