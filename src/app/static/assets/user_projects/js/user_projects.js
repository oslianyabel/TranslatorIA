
var post_form = document.getElementById("new-project-form");
var btn_post = document.getElementById("upload_video_btn_id");
function submit_form(){
  console.log(post_form);
  console.log(btn_post);
  post_form.submit();
}


let up_modal_btn = document.getElementById("new-project");
let dest_l = document.getElementById("t_languages");

// Modal open
up_modal_btn.addEventListener('click', function(event){
  //console.log("Modal open");
  let voice_l = dest_l.value;
  display_voices(voice_l);
});

// Change dest_language
dest_l.addEventListener("change", function (event) {
  //console.log("Changed dest language");
  voice_l = event.target.value;
  display_voices(voice_l);
});

// Change voice gender
$('#voice_gender_clone').change(function(event) {
  // console.log("Changed voice gender to clone");
  // console.log(event);
  // console.log(event.target);
  if(event.target.checked) {
    let voice_l = dest_l.value;
    display_voices(voice_l);
  } 
});
$('#voice_gender_female').change(function(event) {
  // console.log("Changed voice gender to clone");
  // console.log(event);
  // console.log(event.target);
  if(event.target.checked) {
    let voice_l = dest_l.value;
    display_voices(voice_l);
  } 
});
$('#voice_gender_male').change(function(event) {
  // console.log("Changed voice gender to clone");
  // console.log(event);
  // console.log(event.target);
  if(event.target.checked) {
    let voice_l = dest_l.value;
    display_voices(voice_l);
  } 
});


/* ----------  ---------- */
$('#auto-detect-voices_switch').change(function(event) {
  if(event.target.checked) {
    // Hide voice selection
    document.querySelector("#voice_selection").style.display = "none";
    document.querySelector("#auto-detect-voices_switch-on").style.display = "block";
    document.querySelector("#auto-detect-voices_switch-off").style.display = "none";
  } 
  else{    
    // Show voice selection
    document.querySelector("#voice_selection").style.display = "block";
    document.querySelector("#auto-detect-voices_switch-off").style.display = "block";
    document.querySelector("#auto-detect-voices_switch-on").style.display = "none";
  }
});