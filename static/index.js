

var chartDict = {"heartRate":"http://18.234.181.159:5000/chart/heartrate",
                "oxygenLevel":"http://18.234.181.159:5000/chart/oxygen",
                "temperature":"http://18.234.181.159:5000/chart/temperature"}



window.onload = function() {
  console.log(document.getElementById("temp").href);
}
let theme = localStorage.getItem('theme')
if(theme==null)
{
  setTheme('light')
}
else{
  setTheme(theme);
}
let themeDots = document.getElementsByClassName('theme-dot')
for(var i=0;i<themeDots.length;i++)
{
  console.log("working");
  themeDots[i].addEventListener('click',function(){
    let mode = this.dataset.mode
    console.log("Button clicked",mode);
    console.log("Done");
    setTheme(mode)
  })
}
function setTheme(mode)
{
  if(mode=='light'){
    document.getElementById('theme-style').href="/static/default.css"
  }

  if(mode=='orange'){
    document.getElementById('theme-style').href="/static/orange.css"
  }

  if(mode=='green'){
    document.getElementById('theme-style').href="/static/green.css"
  }

  if(mode=='blue'){
    document.getElementById('theme-style').href="/static/blue.css"
  }
  if(mode=='aqua'){
    document.getElementById('theme-style').href="/static/aqua.css"
  }
  localStorage.setItem('theme',mode);
}
