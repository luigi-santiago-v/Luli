function adjustSettingValue(){

    let waterCycleSetting = document.getElementById('waterCycle');
    let waterAmountSetting = document.getElementById('waterAmount');
    let lightCycleSetting = document.getElementById('lightCycle');
    let lightDurationSetting = document.getElementById('lightDuration');

    let waterCycleValue = waterCycleSetting.value;
    let waterAmountValue = waterAmountSetting.value;
    let lightCycleValue = lightCycleSetting.value;
    let lightDurationValue = lightDurationSetting.value;

    document.getElementById("slideLabelTop").innerHTML = waterCycleValue;

    console.log("water: " + waterCycleValue);

}

document.getElementById('waterCycle').addEventListener('onscroll', adjustSettingValue);
document.getElementById('waterAmount').addEventListener('onscroll', adjustSettingValue);
document.getElementById('lightCycle').addEventListener('onscroll', adjustSettingValue);
document.getElementById('lightDuration').addEventListener('onscroll', adjustSettingValue);
