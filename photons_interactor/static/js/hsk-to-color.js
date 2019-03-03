// Taken from http://stackoverflow.com/a/17243070
export default (hue, saturation, kelvin) => {
  function HSLtoHSV(h, s, l) {
    if (arguments.length === 1) {
      (s = h.s), (l = h.l), (h = h.h);
    }
    var _h = h,
      _s,
      _v;

    l *= 2;
    s *= l <= 1 ? l : 2 - l;
    _v = (l + s) / 2;
    _s = (2 * s) / (l + s);

    return {
      h: _h,
      s: _s,
      v: _v
    };
  }

  function HSVtoRGB(h, s, v) {
    var r, g, b, i, f, p, q, t;
    if (arguments.length === 1) {
      (s = h.s), (v = h.v), (h = h.h);
    }
    i = Math.floor(h * 6);
    f = h * 6 - i;
    p = v * (1 - s);
    q = v * (1 - f * s);
    t = v * (1 - (1 - f) * s);
    switch (i % 6) {
      case 0:
        (r = v), (g = t), (b = p);
        break;
      case 1:
        (r = q), (g = v), (b = p);
        break;
      case 2:
        (r = p), (g = v), (b = t);
        break;
      case 3:
        (r = p), (g = q), (b = v);
        break;
      case 4:
        (r = t), (g = p), (b = v);
        break;
      case 5:
        (r = v), (g = p), (b = q);
        break;
    }
    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
  }

  function kelvinToRGB(kelvin) {
    var temperature = kelvin / 100;
    var red;
    if (temperature <= 66) {
      red = 255;
    } else {
      red = temperature - 60;
      red = 329.698727446 * Math.pow(red, -0.1332047592);
      if (red < 0) red = 0;
      if (red > 255) red = 255;
    }

    var green;
    if (temperature <= 66) {
      green = temperature;
      green = 99.4708025861 * Math.log(green) - 161.1195681661;
      if (green < 0) green = 0;
      if (green > 255) green = 255;
    } else {
      green = temperature - 60;
      green = 288.1221695283 * Math.pow(green, -0.0755148492);
      if (green < 0) green = 0;
      if (green > 255) green = 255;
    }

    var blue;
    if (temperature >= 66) {
      blue = 255;
    } else {
      if (temperature <= 19) {
        blue = 0;
      } else {
        blue = temperature - 10;
        blue = 138.5177312231 * Math.log(blue) - 305.0447927307;
        if (blue < 0) blue = 0;
        if (blue > 255) blue = 255;
      }
    }

    return [red, green, blue];
  }

  if (saturation > 0.0) {
    return "hsl(" + hue + ", " + saturation * 100 + "%, 50%)";
  } else {
    var color = kelvinToRGB(kelvin);
    return (
      "rgb(" +
      Math.round(color[0]) +
      ", " +
      Math.round(color[1]) +
      ", " +
      Math.round(color[2]) +
      ")"
    );
  }
};
