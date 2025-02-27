repositories = {
    "ga": "registry.redhat.io",
    "stage": "registry.stage.redhat.io"
    # Add more repositories as needed
}

related_images = ["mta-java-external-provider-rhel9", "mta-generic-external-provider-rhel9",
                  "mta-dotnet-external-provider-rhel8"]
basic_images = ['mta-cli-rhel9']

# Define the URLs for the zip files based on repository types
zip_urls = {
    "stage": "http://download.devel.redhat.com/rcm-guest/staging/jboss-migrationtoolkit/MTA-{ver}.GA/",
    "ga": "http://download.eng.brq.redhat.com/devel/candidates/middleware/migrationtoolkit/MTA-{ver}.GA/"
}
