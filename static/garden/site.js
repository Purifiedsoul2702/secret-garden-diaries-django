'use strict';
const toggle=document.querySelector('.menu-toggle');
const navigation=document.querySelector('#navigation');
if(toggle && navigation) toggle.addEventListener('click',()=>{
 const expanded=toggle.getAttribute('aria-expanded')==='true';
 toggle.setAttribute('aria-expanded',String(!expanded)); navigation.classList.toggle('open',!expanded);
});
document.querySelectorAll('form[data-confirm]').forEach(form=>form.addEventListener('submit',event=>{
 if(!window.confirm(form.dataset.confirm)) event.preventDefault();
}));
