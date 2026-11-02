#target illustrator
app.userInteractionLevel = UserInteractionLevel.DONTDISPLAYALERTS;
var MM = 72/25.4;
var srcDir = new Folder("C:/jjb/src");
var files = srcDir.getFiles("*.*");
var out = new File("C:/jjb/probe.txt"); out.encoding = "UTF-8"; out.open("w");
for (var i = 0; i < files.length; i++) {
  var f = files[i];
  try {
    var d = app.open(f);
    out.writeln("== " + f.name + " | color=" + d.documentColorSpace + " | layers=" + d.layers.length + " | ab=" + d.artboards.length);
    for (var a = 0; a < d.artboards.length; a++) {
      var r = d.artboards[a].artboardRect;
      out.writeln("  AB" + (a+1) + " " + d.artboards[a].name + " L=" + (r[0]/MM).toFixed(1) + " T=" + (r[1]/MM).toFixed(1) + " W=" + ((r[2]-r[0])/MM).toFixed(1) + " H=" + ((r[1]-r[3])/MM).toFixed(1));
    }
    for (var l = 0; l < d.layers.length; l++) {
      var L = d.layers[l];
      out.writeln("  LY '" + L.name + "' vis=" + L.visible + " lock=" + L.locked + " print=" + L.printable + " op=" + L.opacity + " blend=" + L.blendingMode + " items=" + L.pageItems.length + " sub=" + L.layers.length);
    }
    d.close(SaveOptions.DONOTSAVECHANGES);
  } catch (e) { out.writeln("== " + f.name + " ERR " + e); }
}
out.close();
