
let currentLang = localStorage.getItem("language") || "en";

async function loadLanguage(lang){
    const response = await fetch(`/lang/${lang}.json`);
    const texts = await response.json();

    document.querySelectorAll("[data-lang]").forEach(el=>{
        const key = el.getAttribute("data-lang");
        if(texts[key]){
            el.innerHTML = texts[key];
        }
    });

    document.documentElement.dir = lang === "fa" ? "rtl" : "ltr";
    document.documentElement.lang = lang;

    localStorage.setItem("language", lang);
}

function changeLanguage(lang){
    loadLanguage(lang);
}

document.addEventListener("DOMContentLoaded",()=>{
    loadLanguage(currentLang);
});
