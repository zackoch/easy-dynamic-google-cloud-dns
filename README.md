# Easy Dynamic Google Cloud DNS

Makes dynamically updating your google cloud dns records a bit easier ⏩👍😎

If using it as a 'Dynamic DNS' client, it will only make an api call to Google Cloud DNS if there is a required record change instead of needlessly hitting their API.

## Prerequisites

* You must already be using [Google Cloud DNS](https://cloud.google.com/dns/) - this is **not** for [Google Domains Free DNS](https://domains.google.com).
* You must have the ability to create a service account within your Google Cloud Platform console.
* Python version > 3.5.

## Create a Service Account for GCP

* In the Cloud Console, go to the Service Accounts page.
  * [Go to the Service Accounts page](https://console.cloud.google.com/iam-admin/serviceaccounts?_ga=2.22394878.455879836.1607718203-1945110278.1607065052)
* Click **Select a project**, choose a project, and click **Open**.
* Find the row of the service account that you want to create a key for. In that row, click the **More** (three dots) button, and then click **Create key**.
* Select a *Key type* and click *Create*.

Clicking **Create** downloads a service account key file. After you download the key file, you cannot download it again.

**Make sure** to store the key file securely, because it can be used to authenticate as your service account. You can move and rename this file however you would like. Do not store this file publically like on github, or a public facing webserver, or anywhere others that shouldn't can access it.

## Download or clone the repo

### Linux

```bash
git clone https://github.com/zackoch/easy-dynamic-google-cloud-dns.git

cd easy-dynamic-google-cloud-dns

python3 -m venv venv

source venv/bin/activate

pip install -r requirements.txt

deactivate

```

### Windows

```
You're looking at the repo, just download the zip and extract it somwhere on your computer. You'll have to figure out how to make the virtualenv though. I think it's similar to linux (py.exe -m venv venv - then do your pip install -r requirements.txt to get the modules)
```

Move the service account JSON file you downloaded somewhere in this directory or wherever just document the path to it for the next step.

## Edit the config_sample.json file

### Linux

```bash
nano config_sample.json
```

### Windows
```
Open config_sample.json with a text editor
```
The config file looks by default like the one below you need to change some of the values to be specific to your environment.
```json
{
  "api_version": "v1", 
  "gcp_project": "example-project-name",
  "service_account_path": "/path/to/svc_acct.json",
  "ip_api": "https://api64.ipify.org",
  "nameserver": "8.8.8.8",
  "dns_data": [
    {
      "zone": "example-zone",
      "name": "foo.bar.com",
      "type": "A",
      "ttl": 60
    }
  ]
}
```

Key | Value
------------ | -------------
api_version | Just leave this unless you've tested the subsequent versions and know they work. I can confirm v1beta2 works fine as of 12/11/20
gcp_project | This is your project name in GCP when you set up DNS. It can be found on almost every page at the top next to the Google Cloud Platform Logo or just look in the url bar when you're in the dns section and you'll see the name of it after the ?project= parameter
servce_account_path | The full path + filename to the service account file you've created. I've put mine in the main directory as the main.py file, but if you're doing that make sure it's not publically accessable.
ip_api | This is a public 'what's my IP' API without any rate limits. Feel free to use whatever as long as it responds back with text. I suggest using one that supports IPv6 these days...
nameserver | Just leave this as google. If you set this to your local DNS server depending on how frequently you're checking if your IP address changes you could end up in a situation where you constantly are updating your IP via the Google Cloud DNS API until you finally receive the DNS update. Google's DNS servers update within 20 seconds or so of making the changes via the API, so as long as you're not checking any sooner than that you should be good.
dns_data | This IS/CAN be a list. Just make sure you use proper JSON formatting (ie. comma between list items) This is where you'll define all the records you want to update with your current IP address.
zone | This is the dns zone you had to create when setting up google DNS. Each *different tld* will be a different zone if you have multiple domains. the zone name can be found on the main Cloud DNS Zones page within the GCP.
name | This is the actual dns record name you want to change. It can be a regular domain.tld or subdomain. Example: sub1.example.com, example.com **tip**: don't put the trailing `.` after the domain - it's handled in the code (some people will try and put `example.com.` - don't worry about that)
type | This is where you choose the DNS record type. Could be A, AAAA, TXT, whatever, as long as it's valid.
ttl | Thie DNS records Time to Live. Because I use this for dynamically updating DNS where I don't have a static IP address, I set this low to 60 seconds but you can set it to whatever you want. Just know if you set it very high, you may have to wait nearly that long for DNS to propagate.

Don't forget you can put multiple entries under dns_data, just remember to seperate each ```{ }``` block in the list (```[ ]```) with a comma.

## Usage

The way I'm using this is just calling it every 3 minutes from a cron job (Linux). You can totally install run it one off or just initially to create or update a bunch of records too, but it was built to be an easy to use dynamic dns client for your own personal domains.

Use case: Hosting several things out of your house behind a reverse proxy with many subdomains - you'd have to update many dns records every time your IP address changes.

Calling the file straight from the command line with ```python main.py``` after you've activated your virtualenv should be enough to test it. Wait 30 seconds or so and query google's dns server for that domain and it should match your current public IP address.

A smarter way to use this would be to create a cron job like this:

```bash
sudo crontab -e

*/5 * * * * /home/meow/easy-dynamic-google-cloud-dns/venv/bin/python /home/meow/easy-dynamic-google-cloud-dns/main.py
```

You could do something similar using task scheduler in Windows if you're running it on there for some reason.

## License

This project is licensed under the GNU GPLv3
