let currentStep = 1;
const totalSteps = 3;

function showStep(step) {
  document.querySelectorAll('.form-section').forEach(section => section.classList.remove('active'));
  document.getElementById('section' + step).classList.add('active');

  document.querySelectorAll('.step').forEach((el, index) => {
    if (index < step) { el.classList.add('active'); } else { el.classList.remove('active'); }
  });

  document.getElementById('prevBtn').style.display = step === 1 ? 'none' : 'inline-block';
  document.getElementById('nextBtn').style.display = step === totalSteps ? 'none' : 'inline-block';
  document.getElementById('submitBtn').style.display = step === totalSteps ? 'inline-block' : 'none';
}

function nextStep(){ if(currentStep < totalSteps){ currentStep++; showStep(currentStep);} }
function previousStep(){ if(currentStep > 1){ currentStep--; showStep(currentStep);} }

function updateSummary(){
  const timeEl = document.getElementById(formScheduledTimeId);
  const locEl = document.getElementById(formLocationId);
  const maxEl = document.getElementById(formMaxParticipantsId);
  const pubEl = document.getElementById(formIsPublicId);
  const statusEl = document.getElementById(formStatusId);

  if(timeEl) document.getElementById('sumTime').textContent = timeEl.value || initialScheduledTime;
  if(locEl) document.getElementById('sumLocation').textContent = locEl.value || initialLocation;
  if(maxEl) document.getElementById('sumMax').textContent = maxEl.value || initialMaxParticipants;
  if(pubEl) document.getElementById('sumPublic').textContent = pubEl.checked ? 'Public' : 'Private';
  if(statusEl) document.getElementById('sumStatus').textContent = statusEl.options[statusEl.selectedIndex]?.text || initialStatus;
}

document.addEventListener('DOMContentLoaded', function(){
  showStep(1);
  updateSummary();

  [formScheduledTimeId, formLocationId, formMaxParticipantsId, formIsPublicId, formStatusId]
    .forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      const evt = el.tagName === 'SELECT' || el.type === 'checkbox' ? 'change' : 'input';
      el.addEventListener(evt, updateSummary);
    });
});
