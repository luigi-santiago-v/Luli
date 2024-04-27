function generatePlantHTML() {
  return `
  <div id="indPlantSettings" class = "indPlantSettings" >

              <div>
                  <label for="plantType">Plant Type:</label>
                  <select id="plantType" name="plantType">
                          <option value="Spinach">Spinach</option>
                          <option value="Romaine">Romaine</option>
                          <option value="Basil">Basil</option>
                          <option value="Cilantro">Cilantro</option>
                          <option value="Green Onions">Green Onions</option>
                          <option value="Kale">Kale</option>
                          <option value="Mint">Mint</option>
                          <option value="Oregano">Oregano</option>
                          <option value="Parsley">Parsley</option>
                          <option value="Radish">Radish</option>

                  </select>
              </div>

              <div>
                  <label for="start">Date Planted:</label>
                  <input type="date" id="start" name="trip-start" value="2024-01-01" min="2023-01-01" max="2026-12-31" class="custom-calendar"/>
              </div>
              
              <div>
                  <label for="start">Date of Harvest:</label>
                  <input type="date" id="start" na=me="trip-start" value="2024-01-01" min="2023-01-01" max="2026-12-31" />
              </div>
          
              <div>
                  <label for="letters">Choose Container:</label>
                  <select id="letters" name="letters">
                          <option value="A">A</option>
                          <option value="B">B</option>
                          <option value="C">C</option>
                  </select>
              </div>
              
          </div>

     
    `;
}


function updateSettingsCarousel(){

    let plantNumberInput = document.getElementById('quantity');
    let plantNumber = plantNumberInput.value;
    
   
        const plantSettingCarousel = document.getElementById('plantCarousel');
        plantSettingCarousel.innerHTML = ''; // Clear previous content

        for(let i =0;i<plantNumber;i++){
            console.log(i+1);
            const container = generatePlantHTML();
            plantSettingCarousel.insertAdjacentHTML('beforeend', container);
        }


}


