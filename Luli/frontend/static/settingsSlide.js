function adjustSettingValue(){

    let waterCycleSetting = document.getElementById('waterCycle');
    let waterAmountSetting = document.getElementById('waterAmount');
    let lightCycleSetting = document.getElementById('lightCycle');
    let lightDurationSetting = document.getElementById('lightDuration');

    let waterCycleValue = waterCycleSetting.value;
    let waterAmountValue = waterAmountSetting.value;
    let lightCycleValue = lightCycleSetting.value;
    let lightDurationValue = lightDurationSetting.value;

    document.getElementById("waterCycleValue").innerHTML = waterCycleValue;
    document.getElementById("waterAmountValue").innerHTML = waterAmountValue;
    document.getElementById("lightCycleValue").innerHTML = lightCycleValue;
    document.getElementById("lightDurationValue").innerHTML = lightDurationValue;

    let data = {
        waterCycle: { label: 'Water Cycle', value: waterCycleValue },
        waterAmount: { label: 'Water Amount', value: waterAmountValue },
        lightCycle: { label: 'Light Cycle', value: lightCycleValue },
        lightDuration: { label: 'Light Duration', value: lightDurationValue }
    };

    fetch('/save_settings', 
    {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })


}

document.getElementById('waterCycle').addEventListener('input', adjustSettingValue);
document.getElementById('waterAmount').addEventListener('input', adjustSettingValue);
document.getElementById('lightCycle').addEventListener('input', adjustSettingValue);
document.getElementById('lightDuration').addEventListener('input', adjustSettingValue);
