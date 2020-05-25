var nodemailer = require('nodemailer');
const fs = require('fs');

require.extensions['.html'] = function (module, filename) {
  module.exports = fs.readFileSync(filename, 'utf8');
};

var data = require('./formverifica.html')


  var transport = nodemailer.createTransport({ //creato utilizzando mailTrap
    host: "smtp.mailtrap.io",
    port: 2525,
    auth: {
      user: "342b4ff1a86cda",
      pass: "fdd9fec0eb3081"
    }
  });


  var mailOptions = {
    from: '"Example Team" <from@example.com>',
    to: 'meban83455@prowerl.com',
    subject: 'Sending Email using Node.js',
    text: 'This email is sent to verify your iTedx new account.\nPlease click on the button below.',
    html: data

    };
  
  transport.sendMail(mailOptions, function(error, info){
    if (error) {
      console.log(error);
    } else {
      console.log('Email sent: ' + info.response);
    }
  });