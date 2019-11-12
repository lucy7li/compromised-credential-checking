// Generated by CoffeeScript 2.3.2
(function() {
  var Util;

  Util = class Util {
    static assertNumber(val, desc) {
      if (val == null) {
        throw new Error(desc + ' is required.');
      }
      if (typeof val !== 'number') {
        throw new Error(desc + ' must be a number.');
      }
    }

    static assertOrder(start, end, startName, endName, desc) {
      if (start >= end) {
        throw new Error(`${desc}: ${startName}(${start}) must be smaller than ${endName}(${end}).`);
      }
    }

  };

  module.exports = Util;

}).call(this);
