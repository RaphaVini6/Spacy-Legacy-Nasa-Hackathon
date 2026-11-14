using System.Text.Json;
using System.Text.Json.Serialization;
using Backend.Models;

namespace Backend.Services;

// Loads Data/*.json in memory. TODO: move to a database if the data grows.
public class DataStore
{
    public static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNameCaseInsensitive = true,
        Converters = { new JsonStringEnumConverter() },
    };

    public IReadOnlyList<ProbeData> Probes { get; }

    public DataStore(IWebHostEnvironment env)
    {
        var dir = Path.Combine(env.ContentRootPath, "Data");
        // probes are split by destination: probes.moon.json, probes.mars.json, ...
        Probes = Directory.GetFiles(dir, "probes.*.json").Order()
            .SelectMany(f => JsonSerializer.Deserialize<List<ProbeData>>(File.ReadAllText(f), JsonOptions) ?? [])
            .OrderBy(p => p.Destination).ThenBy(p => p.Date)
            .ToList();
    }

    public ProbeData? Probe(string id) => Probes.FirstOrDefault(p => p.Id.Equals(id, StringComparison.OrdinalIgnoreCase));
}
