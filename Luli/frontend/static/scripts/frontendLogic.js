let meter = {
   type: "none",
   data: "none",
   unit: "none",

   set data(x) {
       this._data = x;
   },
   get data() {
       return this._data;
   },
   set type(x) {
       this._type = x;
   },
   get type() {
       return this._type;
   },

   printData: function () {
       console.log(this.type + " Level: " + this.data + " " + this.unit);
   }
};

meter.data = 10;
meter.type = "Water";
meter.printData();
