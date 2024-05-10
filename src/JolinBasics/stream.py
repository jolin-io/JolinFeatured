### A Pluto.jl notebook ###
# v0.19.28
# Welcome to your Python reactive notebook.
from juliacall import Main as _jl

# This Pluto notebook uses `format_html`, `MD` and `HTML` to build rich outputs inside Pluto. For running this notebook outside of Pluto, the following definitions are important.
format_html = _jl.seval('format_html(ans) = repr("text/html", ans)')
HTML = _jl.seval("HTML")
MD = _jl.seval('''begin
    import CommonMark
    parser = CommonMark.Parser()
    CommonMark.enable!(parser, CommonMark.DollarMathRule())
    CommonMark.enable!(parser, CommonMark.TableRule())
    parser
end''')

# This Pluto notebook uses `bind('xyz', ...)` for interactivity. When running this notebook outside of Pluto, the following 'mock version' of `bind` gives bound variables a default value (instead of an error).
# setup julia reference to python globals (This works both from julia as well as from Python)
_jl.seval('''function(glo)
    @eval const pyglobals=$glo
end''')(globals())
# create the bind fallback function
bind = _jl.seval('''begin
    function bind(name, ui)
        initial_value_getter = try
            Base.loaded_modules[Base.PkgId(Base.UUID("6e696c72-6542-2067-7265-42206c756150"), "AbstractPlutoDingetjes")].Bonds.initial_value
        catch
            b -> missing
        end
        initial_value = Core.applicable(Base.get, ui) ? Base.get(ui) : initial_value_getter(ui)
        pyglobals[name] = initial_value
        ui
    end
end''')

# ╔═╡ 040b90c8-8ed3-4497-866a-bed69b2e27e1
from juliacall import Main as jl
jl.seval("using Dates")
JolinPluto = jl.seval("import JolinPluto; JolinPluto")
PlutoUI = jl.seval("import PlutoUI; PlutoUI")
JolinPluto.output_below()

# ╔═╡ 172fbef1-3f9e-4ca2-bdc5-8d2755d62c34
MD("""
# Self-updating Reactive Notebooks

This is a small introduction about how to include and process continuous updates right in your reactive notebook.
""")

# ╔═╡ 35229634-2c40-4de9-8911-a61ceb32f663
MD("""
We are simulating **financial data** (also called random walk) which is streamed onto a python queue, read from it, and processed.

You should be able to take this demo and adapt to whatever continuous updates you may have at your company.
""")

# ╔═╡ fa392c32-7ed6-11ee-02d6-e5f4f5490be6
import queue
import threading
import time
import random
import math
from collections import deque
from matplotlib import pyplot as plt

# ╔═╡ 83f49510-e63b-45af-9c5e-0686f10d154f
PlutoUI.TableOfContents()

# ╔═╡ a421c2ba-f2b4-463a-bfb1-e05e5879e918
MD("""
##  Create updates

The simplest way to create updates is to create a queue and ...
- start a separate thread to look for updates
- if there is an update put it onto the queue.
""")

# ╔═╡ 6ffa64f4-0126-4536-912f-387d4ad9bbf5
q = queue.Queue(maxsize=2)

# ╔═╡ e4b67d9e-b974-470e-ab59-20f04117deb1
def thread_queueput_random(stop_event):
	while not stop_event.is_set():
		x = random.gauss()
		q.put(x)
		time.sleep(2)

# ╔═╡ 7e148569-41e8-444f-a039-f5e91839bcfc
stop_event = JolinPluto.start_python_thread(thread_queueput_random)

# ╔═╡ ad6a5da9-304c-4d09-b59f-c35c31123b18
MD("""
Your queue is now filling up.
""")

# ╔═╡ 07e65d43-6f09-4221-acfb-de05a64283e6
MD("""
## Fetch updates

Having a channel full of updates, we can make Pluto read updates again and again and again.<br/>
🪄 It is like magic 🪄

You can even disable updates for some time by opening the cell *menu* (the three dots top-right in the cell) and choose *Disable Cell*.
""")

# ╔═╡ ff1a1833-a060-4939-bf96-50d6bbc2b974
update = JolinPluto.repeat_queueget(q)

# ╔═╡ d8f62255-a239-45bc-8042-0eda43caff8a
MD("""
Let's collect these updates.
""")

# ╔═╡ 97fcba32-bbca-4570-a4da-4a8438a5e10f
maxlen = 20
first_element = 0.0
bounded_collection = deque([first_element], maxlen)

# ╔═╡ c0afe0d1-3eb8-4274-b4cc-018097d1bdb2
MD("""
## User Interfaces

Let's control `shift` and `variance` using user inputs.
""")

# ╔═╡ 09f75fd2-6096-48d5-8f80-fd775e01025f
ui1 = bind("shift", PlutoUI.Slider([-3, -1, 0, 1, 3], default=0, show_value=True))
ui2 = bind("variance", PlutoUI.Slider([1, 2, 10, 100], default=1, show_value=True))
ui1, ui2

# ╔═╡ 5095d2c5-7b3c-4cb7-b694-d7ce4b32fd90
noise = update * math.sqrt(variance) + shift
prev_element = bounded_collection[-1]
next_element = prev_element + noise

bounded_collection.append(next_element)
bounded_collection

# ╔═╡ 34eb23e8-b0a6-4edc-911b-bedd8dd0a232
MD("""
The above two lines create ui elements which update `shift` and `variance` respectively.

You can try it by moving the above sliders.
""")

# ╔═╡ 149ee90f-d5ea-4791-8bad-3f3f260d9f28
shift, variance

# ╔═╡ b6d0153c-e777-421f-8699-02340e0ad273
MD("""
You can combine multiple input elements into arbitrary Markdown or HTML.
""")

# ╔═╡ da871125-8067-4441-b5df-d76d609bc46d
# The <>...</> wrapper is needed because most MD parsers don't parse inline html well. Using <>...</> is our super useful little extension.
choose = MD(f'''
|          | choose                  |
|----------|:------------------------|
| shift    | <>{format_html(ui1)}</> |
| variance | <>{format_html(ui2)}</> |
''')

# ╔═╡ 16609b7c-0fa7-41d3-8dd4-4a99aaeeb0d7
choose

# ╔═╡ 10246e4d-66e3-41fb-b92c-4900e0d5454b
MD("""
## Plotting

Finally we build or graph.
""")

# ╔═╡ 5f277b91-20ef-448c-83f8-3ee504644f3b
# depend on update to auto trigger this cells
update
figure, ax = plt.subplots()
ax.plot(bounded_collection)
figure

# ╔═╡ 60a9e137-1f35-4268-ad10-be6104431e04
figure

# ╔═╡ e232f3f9-9687-4b1a-9428-47f9aef9ec6b
MD("""
# Next

- take a look at the other example notebooks

That was probably your first streaming report ever 😎.
""")

# ╔═╡ 6a1f8649-eb6b-47b5-bae2-b834f7f79f69
MD("""
# Memory tracking

For long running notebooks, it is important to make sure that no memory leaks appear.
""")

# ╔═╡ 0316b6ed-5fa7-41e1-8230-616150c3b2a0
memory_tracking = deque([], 400)

# ╔═╡ 7d670f9f-6fd5-40fa-ac82-4a6b034a2b7c
MD("""
We use some julia code for time manipulations. It automatically converts to datetimes. 
""")

# ╔═╡ bc23101c-fdee-4fa8-a2e0-105d73eeefb5
def next_time_rounded_by_X_seconds(x):
	return jl.ceil(jl.now(), jl.Second(x))

dtime = next_time_rounded_by_X_seconds(10)
dtime, dtime.minute

# ╔═╡ 36679b5b-5fcc-499b-bd0e-74556d34daf3
# magic to repeat this very cell every 10 seconds
JolinPluto.repeat_at(next_time_rounded_by_X_seconds(10))

# run Garbage Collector (it is recommended to run both versions)
jl.GC.gc(True); jl.GC.gc(False)  
memory_tracking.append(jl.Base.gc_live_bytes() / 2**20)

figure2, ax2 = plt.subplots()
ax2.plot(memory_tracking)
ax2.set_ylabel("MB")
figure2

# ╔═╡ 00000000-0000-0000-0000-000000000001
PLUTO_PROJECT_TOML_CONTENTS = """
[deps]
CommonMark = "a80b9123-70ca-4bc0-993e-6e3bcb318db6"
CondaPkg = "992eb4ea-22a4-4c89-a5bb-47a3300528ab"
Dates = "ade2ca70-3891-5945-98fb-dc099432e06a"
JolinPluto = "5b0b4ef8-f4e6-4363-b674-3f031f7b9530"
PlutoUI = "7f904dfe-b85e-4ff6-b463-dae2292396a8"
PythonCall = "6099a3de-0909-46bc-b1f4-468b9a2dfc0d"

[compat]
CommonMark = "~0.8.12"
CondaPkg = "~0.2.22"
JolinPluto = "~0.1.58"
PlutoUI = "~0.7.54"
PythonCall = "~0.9.15"
"""

# ╔═╡ 00000000-0000-0000-0000-000000000002
PLUTO_MANIFEST_TOML_CONTENTS = """
# This file is machine-generated - editing it directly is not advised

julia_version = "1.9.4"
manifest_format = "2.0"
project_hash = "c1f70bcdae1c24af50e9e5dcfcd1482c74815bf5"

[[deps.AbstractPlutoDingetjes]]
deps = ["Pkg"]
git-tree-sha1 = "793501dcd3fa7ce8d375a2c878dca2296232686e"
uuid = "6e696c72-6542-2067-7265-42206c756150"
version = "1.2.2"

[[deps.ArgTools]]
uuid = "0dad84c5-d112-42e6-8d28-ef12dabb789f"
version = "1.1.1"

[[deps.Artifacts]]
uuid = "56f22d72-fd6d-98f1-02f0-08ddc0907c33"

[[deps.Base64]]
uuid = "2a0f44e3-6c83-55bd-87e4-b1978d98bd5f"

[[deps.BitFlags]]
git-tree-sha1 = "2dc09997850d68179b69dafb58ae806167a32b1b"
uuid = "d1d4a3ce-64b1-5f1a-9ba4-7e7e69966f35"
version = "0.1.8"

[[deps.CodecZlib]]
deps = ["TranscodingStreams", "Zlib_jll"]
git-tree-sha1 = "cd67fc487743b2f0fd4380d4cbd3a24660d0eec8"
uuid = "944b1d66-785c-5afd-91f1-9de20f533193"
version = "0.7.3"

[[deps.ColorTypes]]
deps = ["FixedPointNumbers", "Random"]
git-tree-sha1 = "eb7f0f8307f71fac7c606984ea5fb2817275d6e4"
uuid = "3da002f7-5984-5a60-b8a6-cbb66c0b333f"
version = "0.11.4"

[[deps.CommonMark]]
deps = ["Crayons", "JSON", "PrecompileTools", "URIs"]
git-tree-sha1 = "532c4185d3c9037c0237546d817858b23cf9e071"
uuid = "a80b9123-70ca-4bc0-993e-6e3bcb318db6"
version = "0.8.12"

[[deps.Compat]]
deps = ["UUIDs"]
git-tree-sha1 = "8a62af3e248a8c4bad6b32cbbe663ae02275e32c"
uuid = "34da2185-b29b-5c13-b0c7-acf172513d20"
version = "4.10.0"
weakdeps = ["Dates", "LinearAlgebra"]

    [deps.Compat.extensions]
    CompatLinearAlgebraExt = "LinearAlgebra"

[[deps.CompilerSupportLibraries_jll]]
deps = ["Artifacts", "Libdl"]
uuid = "e66e0078-7015-5450-92f7-15fbd957f2ae"
version = "1.0.5+0"

[[deps.ConcurrentUtilities]]
deps = ["Serialization", "Sockets"]
git-tree-sha1 = "8cfa272e8bdedfa88b6aefbbca7c19f1befac519"
uuid = "f0e56b4a-5159-44fe-b623-3e5288b988bb"
version = "2.3.0"

[[deps.CondaPkg]]
deps = ["JSON3", "Markdown", "MicroMamba", "Pidfile", "Pkg", "Preferences", "TOML"]
git-tree-sha1 = "e81c4263c7ef4eca4d645ef612814d72e9255b41"
uuid = "992eb4ea-22a4-4c89-a5bb-47a3300528ab"
version = "0.2.22"

[[deps.Continuables]]
deps = ["DataTypesBasic", "ExprParsers", "OrderedCollections", "SimpleMatch"]
git-tree-sha1 = "96107b5ecb77d0397395cec4a95a28873e124204"
uuid = "79afa230-ca09-11e8-120b-5decf7bf5e25"
version = "1.0.3"

[[deps.Crayons]]
git-tree-sha1 = "249fe38abf76d48563e2f4556bebd215aa317e15"
uuid = "a8cc5b0e-0ffa-5ad4-8c14-923d3ee1735f"
version = "4.1.1"

[[deps.DataAPI]]
git-tree-sha1 = "8da84edb865b0b5b0100c0666a9bc9a0b71c553c"
uuid = "9a962f9c-6df0-11e9-0e5d-c546b8b5ee8a"
version = "1.15.0"

[[deps.DataTypesBasic]]
git-tree-sha1 = "0ebf9d9def6135849a9da8d2a1f144d0c467b81c"
uuid = "83eed652-29e8-11e9-12da-a7c29d64ffc9"
version = "2.0.3"

[[deps.DataValueInterfaces]]
git-tree-sha1 = "bfc1187b79289637fa0ef6d4436ebdfe6905cbd6"
uuid = "e2d170a0-9d28-54be-80f0-106bbe20a464"
version = "1.0.0"

[[deps.Dates]]
deps = ["Printf"]
uuid = "ade2ca70-3891-5945-98fb-dc099432e06a"

[[deps.Downloads]]
deps = ["ArgTools", "FileWatching", "LibCURL", "NetworkOptions"]
uuid = "f43a241f-c20a-4ad4-852c-f6b1247861c6"
version = "1.6.0"

[[deps.ExceptionUnwrapping]]
deps = ["Test"]
git-tree-sha1 = "e90caa41f5a86296e014e148ee061bd6c3edec96"
uuid = "460bff9d-24e4-43bc-9d9f-a8973cb893f4"
version = "0.1.9"

[[deps.Expat_jll]]
deps = ["Artifacts", "JLLWrappers", "Libdl"]
git-tree-sha1 = "4558ab818dcceaab612d1bb8c19cee87eda2b83c"
uuid = "2e619515-83b5-522b-bb60-26c02a35a201"
version = "2.5.0+0"

[[deps.ExprParsers]]
deps = ["ProxyInterfaces", "SimpleMatch", "StructEquality"]
git-tree-sha1 = "d7508fa0337cee19e380ad5fbc7ac698ecc471ba"
uuid = "c5caad1f-83bd-4ce8-ac8e-4b29921e994e"
version = "1.2.3"

[[deps.FileWatching]]
uuid = "7b1f6079-737a-58dc-b8bc-7a2ca5c1b5ee"

[[deps.FixedPointNumbers]]
deps = ["Statistics"]
git-tree-sha1 = "335bfdceacc84c5cdf16aadc768aa5ddfc5383cc"
uuid = "53c48c17-4a7d-5ca2-90c5-79b7896eea93"
version = "0.8.4"

[[deps.Git]]
deps = ["Git_jll"]
git-tree-sha1 = "51764e6c2e84c37055e846c516e9015b4a291c7d"
uuid = "d7ba0133-e1db-5d97-8f8c-041e4b3a1eb2"
version = "1.3.0"

[[deps.Git_jll]]
deps = ["Artifacts", "Expat_jll", "JLLWrappers", "LibCURL_jll", "Libdl", "Libiconv_jll", "OpenSSL_jll", "PCRE2_jll", "Zlib_jll"]
git-tree-sha1 = "bb8f7cc77ec1152414b2af6db533d9471cfbb2d1"
uuid = "f8c6e375-362e-5223-8a59-34ff63f689eb"
version = "2.42.0+0"

[[deps.HTTP]]
deps = ["Base64", "CodecZlib", "ConcurrentUtilities", "Dates", "ExceptionUnwrapping", "Logging", "LoggingExtras", "MbedTLS", "NetworkOptions", "OpenSSL", "Random", "SimpleBufferStream", "Sockets", "URIs", "UUIDs"]
git-tree-sha1 = "5eab648309e2e060198b45820af1a37182de3cce"
uuid = "cd3eb016-35fb-5094-929b-558a96fad6f3"
version = "1.10.0"

[[deps.Hyperscript]]
deps = ["Test"]
git-tree-sha1 = "8d511d5b81240fc8e6802386302675bdf47737b9"
uuid = "47d2ed2b-36de-50cf-bf87-49c2cf4b8b91"
version = "0.0.4"

[[deps.HypertextLiteral]]
deps = ["Tricks"]
git-tree-sha1 = "7134810b1afce04bbc1045ca1985fbe81ce17653"
uuid = "ac1192a8-f4b3-4bfe-ba22-af5b92cd3ab2"
version = "0.9.5"

[[deps.IOCapture]]
deps = ["Logging", "Random"]
git-tree-sha1 = "d75853a0bdbfb1ac815478bacd89cd27b550ace6"
uuid = "b5f81e59-6552-4d32-b1f0-c071b021bf89"
version = "0.2.3"

[[deps.InteractiveUtils]]
deps = ["Markdown"]
uuid = "b77e0a4c-d291-57a0-90e8-8db25a27a240"

[[deps.IteratorInterfaceExtensions]]
git-tree-sha1 = "a3f24677c21f5bbe9d2a714f95dcd58337fb2856"
uuid = "82899510-4779-5014-852e-03e436cf321d"
version = "1.0.0"

[[deps.JLLWrappers]]
deps = ["Artifacts", "Preferences"]
git-tree-sha1 = "7e5d6779a1e09a36db2a7b6cff50942a0a7d0fca"
uuid = "692b3bcd-3c85-4b1f-b108-f13ce0eb3210"
version = "1.5.0"

[[deps.JSON]]
deps = ["Dates", "Mmap", "Parsers", "Unicode"]
git-tree-sha1 = "31e996f0a15c7b280ba9f76636b3ff9e2ae58c9a"
uuid = "682c06a0-de6a-54ab-a142-c8b1cf79cde6"
version = "0.21.4"

[[deps.JSON3]]
deps = ["Dates", "Mmap", "Parsers", "PrecompileTools", "StructTypes", "UUIDs"]
git-tree-sha1 = "95220473901735a0f4df9d1ca5b171b568b2daa3"
uuid = "0f8b85d8-7281-11e9-16c2-39a750bddbf1"
version = "1.13.2"

[[deps.JWTs]]
deps = ["Base64", "Downloads", "JSON", "MbedTLS", "Random"]
git-tree-sha1 = "4b4111b7d649426874d4eec78f87871f90f8e541"
uuid = "d850fbd6-035d-5a70-a269-1ca2e636ac6c"
version = "0.2.3"

[[deps.JolinPluto]]
deps = ["AbstractPlutoDingetjes", "Base64", "Continuables", "Dates", "Git", "HTTP", "HypertextLiteral", "JSON3", "JWTs", "UUIDs"]
git-tree-sha1 = "5406ce394a65b8e01c160da059ab11b7bb6e1d15"
uuid = "5b0b4ef8-f4e6-4363-b674-3f031f7b9530"
version = "0.1.58"

    [deps.JolinPluto.extensions]
    AWSExt = "AWS"
    PlotsExt = "Plots"
    PythonExt = "PythonCall"
    RCallExt = "RCall"

    [deps.JolinPluto.weakdeps]
    AWS = "fbe9abb3-538b-5e4e-ba9e-bc94f4f92ebc"
    Plots = "91a5bcdd-55d7-5caf-9e0b-520d859cae80"
    PythonCall = "6099a3de-0909-46bc-b1f4-468b9a2dfc0d"
    RCall = "6f49c342-dc21-5d91-9882-a32aef131414"

[[deps.LazyArtifacts]]
deps = ["Artifacts", "Pkg"]
uuid = "4af54fe1-eca0-43a8-85a7-787d91b784e3"

[[deps.LibCURL]]
deps = ["LibCURL_jll", "MozillaCACerts_jll"]
uuid = "b27032c2-a3e7-50c8-80cd-2d36dbcbfd21"
version = "0.6.4"

[[deps.LibCURL_jll]]
deps = ["Artifacts", "LibSSH2_jll", "Libdl", "MbedTLS_jll", "Zlib_jll", "nghttp2_jll"]
uuid = "deac9b47-8bc7-5906-a0fe-35ac56dc84c0"
version = "8.4.0+0"

[[deps.LibGit2]]
deps = ["Base64", "NetworkOptions", "Printf", "SHA"]
uuid = "76f85450-5226-5b5a-8eaa-529ad045b433"

[[deps.LibSSH2_jll]]
deps = ["Artifacts", "Libdl", "MbedTLS_jll"]
uuid = "29816b5a-b9ab-546f-933c-edad1886dfa8"
version = "1.11.0+1"

[[deps.Libdl]]
uuid = "8f399da3-3557-5675-b5ff-fb832c97cbdb"

[[deps.Libiconv_jll]]
deps = ["Artifacts", "JLLWrappers", "Libdl"]
git-tree-sha1 = "f9557a255370125b405568f9767d6d195822a175"
uuid = "94ce4f54-9a6c-5748-9c1c-f9c7231a4531"
version = "1.17.0+0"

[[deps.LinearAlgebra]]
deps = ["Libdl", "OpenBLAS_jll", "libblastrampoline_jll"]
uuid = "37e2e46d-f89d-539d-b4ee-838fcccc9c8e"

[[deps.Logging]]
uuid = "56ddb016-857b-54e1-b83d-db4d58db5568"

[[deps.LoggingExtras]]
deps = ["Dates", "Logging"]
git-tree-sha1 = "c1dd6d7978c12545b4179fb6153b9250c96b0075"
uuid = "e6f89c97-d47a-5376-807f-9c37f3926c36"
version = "1.0.3"

[[deps.MIMEs]]
git-tree-sha1 = "65f28ad4b594aebe22157d6fac869786a255b7eb"
uuid = "6c6e2e6c-3030-632d-7369-2d6c69616d65"
version = "0.1.4"

[[deps.MacroTools]]
deps = ["Markdown", "Random"]
git-tree-sha1 = "9ee1618cbf5240e6d4e0371d6f24065083f60c48"
uuid = "1914dd2f-81c6-5fcd-8719-6d5c9610ff09"
version = "0.5.11"

[[deps.Markdown]]
deps = ["Base64"]
uuid = "d6f4376e-aef5-505a-96c1-9c027394607a"

[[deps.MbedTLS]]
deps = ["Dates", "MbedTLS_jll", "MozillaCACerts_jll", "NetworkOptions", "Random", "Sockets"]
git-tree-sha1 = "c067a280ddc25f196b5e7df3877c6b226d390aaf"
uuid = "739be429-bea8-5141-9913-cc70e7f3736d"
version = "1.1.9"

[[deps.MbedTLS_jll]]
deps = ["Artifacts", "Libdl"]
uuid = "c8ffd9c3-330d-5841-b78e-0817d7145fa1"
version = "2.28.2+0"

[[deps.MicroMamba]]
deps = ["Pkg", "Scratch", "micromamba_jll"]
git-tree-sha1 = "011cab361eae7bcd7d278f0a7a00ff9c69000c51"
uuid = "0b3b1443-0f03-428d-bdfb-f27f9c1191ea"
version = "0.1.14"

[[deps.Mmap]]
uuid = "a63ad114-7e13-5084-954f-fe012c677804"

[[deps.MozillaCACerts_jll]]
uuid = "14a3606d-f60d-562e-9121-12d972cd8159"
version = "2022.10.11"

[[deps.NetworkOptions]]
uuid = "ca575930-c2e3-43a9-ace4-1e988b2c1908"
version = "1.2.0"

[[deps.OpenBLAS_jll]]
deps = ["Artifacts", "CompilerSupportLibraries_jll", "Libdl"]
uuid = "4536629a-c528-5b80-bd46-f80d51c5b363"
version = "0.3.21+4"

[[deps.OpenSSL]]
deps = ["BitFlags", "Dates", "MozillaCACerts_jll", "OpenSSL_jll", "Sockets"]
git-tree-sha1 = "51901a49222b09e3743c65b8847687ae5fc78eb2"
uuid = "4d8831e6-92b7-49fb-bdf8-b643e874388c"
version = "1.4.1"

[[deps.OpenSSL_jll]]
deps = ["Artifacts", "JLLWrappers", "Libdl"]
git-tree-sha1 = "cc6e1927ac521b659af340e0ca45828a3ffc748f"
uuid = "458c3c95-2e84-50aa-8efc-19380b2a3a95"
version = "3.0.12+0"

[[deps.OrderedCollections]]
git-tree-sha1 = "2e73fe17cac3c62ad1aebe70d44c963c3cfdc3e3"
uuid = "bac558e1-5e72-5ebc-8fee-abe8a469f55d"
version = "1.6.2"

[[deps.PCRE2_jll]]
deps = ["Artifacts", "Libdl"]
uuid = "efcefdf7-47ab-520b-bdef-62a2eaa19f15"
version = "10.42.0+0"

[[deps.Parsers]]
deps = ["Dates", "PrecompileTools", "UUIDs"]
git-tree-sha1 = "a935806434c9d4c506ba941871b327b96d41f2bf"
uuid = "69de0a69-1ddd-5017-9359-2bf0b02dc9f0"
version = "2.8.0"

[[deps.Pidfile]]
deps = ["FileWatching", "Test"]
git-tree-sha1 = "2d8aaf8ee10df53d0dfb9b8ee44ae7c04ced2b03"
uuid = "fa939f87-e72e-5be4-a000-7fc836dbe307"
version = "1.3.0"

[[deps.Pkg]]
deps = ["Artifacts", "Dates", "Downloads", "FileWatching", "LibGit2", "Libdl", "Logging", "Markdown", "Printf", "REPL", "Random", "SHA", "Serialization", "TOML", "Tar", "UUIDs", "p7zip_jll"]
uuid = "44cfe95a-1eb2-52ea-b672-e2afdf69b78f"
version = "1.9.2"

[[deps.PlutoUI]]
deps = ["AbstractPlutoDingetjes", "Base64", "ColorTypes", "Dates", "FixedPointNumbers", "Hyperscript", "HypertextLiteral", "IOCapture", "InteractiveUtils", "JSON", "Logging", "MIMEs", "Markdown", "Random", "Reexport", "URIs", "UUIDs"]
git-tree-sha1 = "bd7c69c7f7173097e7b5e1be07cee2b8b7447f51"
uuid = "7f904dfe-b85e-4ff6-b463-dae2292396a8"
version = "0.7.54"

[[deps.PrecompileTools]]
deps = ["Preferences"]
git-tree-sha1 = "03b4c25b43cb84cee5c90aa9b5ea0a78fd848d2f"
uuid = "aea7be01-6a6a-4083-8856-8a6e6704d82a"
version = "1.2.0"

[[deps.Preferences]]
deps = ["TOML"]
git-tree-sha1 = "00805cd429dcb4870060ff49ef443486c262e38e"
uuid = "21216c6a-2e73-6563-6e65-726566657250"
version = "1.4.1"

[[deps.Printf]]
deps = ["Unicode"]
uuid = "de0858da-6303-5e67-8744-51eddeeeb8d7"

[[deps.ProxyInterfaces]]
git-tree-sha1 = "848a4470b54820cba8c4642840e9cea8345ff520"
uuid = "9b3bf0c4-f070-48bc-ae01-f2584e9c23bc"
version = "1.1.1"

[[deps.PythonCall]]
deps = ["CondaPkg", "Dates", "Libdl", "MacroTools", "Markdown", "Pkg", "REPL", "Requires", "Serialization", "Tables", "UnsafePointers"]
git-tree-sha1 = "4999b3e4e9bdeba0b61ede19cc45a2128db21cdc"
uuid = "6099a3de-0909-46bc-b1f4-468b9a2dfc0d"
version = "0.9.15"

[[deps.REPL]]
deps = ["InteractiveUtils", "Markdown", "Sockets", "Unicode"]
uuid = "3fa0cd96-eef1-5676-8a61-b3b8758bbffb"

[[deps.Random]]
deps = ["SHA", "Serialization"]
uuid = "9a3f8284-a2c9-5f02-9a11-845980a1fd5c"

[[deps.Reexport]]
git-tree-sha1 = "45e428421666073eab6f2da5c9d310d99bb12f9b"
uuid = "189a3867-3050-52da-a836-e630ba90ab69"
version = "1.2.2"

[[deps.Requires]]
deps = ["UUIDs"]
git-tree-sha1 = "838a3a4188e2ded87a4f9f184b4b0d78a1e91cb7"
uuid = "ae029012-a4dd-5104-9daa-d747884805df"
version = "1.3.0"

[[deps.SHA]]
uuid = "ea8e919c-243c-51af-8825-aaa63cd721ce"
version = "0.7.0"

[[deps.Scratch]]
deps = ["Dates"]
git-tree-sha1 = "3bac05bc7e74a75fd9cba4295cde4045d9fe2386"
uuid = "6c6a2e73-6563-6170-7368-637461726353"
version = "1.2.1"

[[deps.Serialization]]
uuid = "9e88b42a-f829-5b0c-bbe9-9e923198166b"

[[deps.SimpleBufferStream]]
git-tree-sha1 = "874e8867b33a00e784c8a7e4b60afe9e037b74e1"
uuid = "777ac1f9-54b0-4bf8-805c-2214025038e7"
version = "1.1.0"

[[deps.SimpleMatch]]
git-tree-sha1 = "78750b67a6cb3b6140be99f2fb56ae26ad28104b"
uuid = "a3ae8450-d22f-11e9-3fe0-77240e25996f"
version = "1.1.0"

[[deps.Sockets]]
uuid = "6462fe0b-24de-5631-8697-dd941f90decc"

[[deps.SparseArrays]]
deps = ["Libdl", "LinearAlgebra", "Random", "Serialization", "SuiteSparse_jll"]
uuid = "2f01184e-e22b-5df5-ae63-d93ebab69eaf"

[[deps.Statistics]]
deps = ["LinearAlgebra", "SparseArrays"]
uuid = "10745b16-79ce-11e8-11f9-7d13ad32a3b2"
version = "1.9.0"

[[deps.StructEquality]]
deps = ["Compat"]
git-tree-sha1 = "192a9f1de3cfef80ab1a4ba7b150bb0e11ceedcf"
uuid = "6ec83bb0-ed9f-11e9-3b4c-2b04cb4e219c"
version = "2.1.0"

[[deps.StructTypes]]
deps = ["Dates", "UUIDs"]
git-tree-sha1 = "ca4bccb03acf9faaf4137a9abc1881ed1841aa70"
uuid = "856f2bd8-1eba-4b0a-8007-ebc267875bd4"
version = "1.10.0"

[[deps.SuiteSparse_jll]]
deps = ["Artifacts", "Libdl", "Pkg", "libblastrampoline_jll"]
uuid = "bea87d4a-7f5b-5778-9afe-8cc45184846c"
version = "5.10.1+6"

[[deps.TOML]]
deps = ["Dates"]
uuid = "fa267f1f-6049-4f14-aa54-33bafae1ed76"
version = "1.0.3"

[[deps.TableTraits]]
deps = ["IteratorInterfaceExtensions"]
git-tree-sha1 = "c06b2f539df1c6efa794486abfb6ed2022561a39"
uuid = "3783bdb8-4a98-5b6b-af9a-565f29a5fe9c"
version = "1.0.1"

[[deps.Tables]]
deps = ["DataAPI", "DataValueInterfaces", "IteratorInterfaceExtensions", "LinearAlgebra", "OrderedCollections", "TableTraits"]
git-tree-sha1 = "cb76cf677714c095e535e3501ac7954732aeea2d"
uuid = "bd369af6-aec1-5ad0-b16a-f7cc5008161c"
version = "1.11.1"

[[deps.Tar]]
deps = ["ArgTools", "SHA"]
uuid = "a4e569a6-e804-4fa4-b0f3-eef7a1d5b13e"
version = "1.10.0"

[[deps.Test]]
deps = ["InteractiveUtils", "Logging", "Random", "Serialization"]
uuid = "8dfed614-e22c-5e08-85e1-65c5234f0b40"

[[deps.TranscodingStreams]]
git-tree-sha1 = "1fbeaaca45801b4ba17c251dd8603ef24801dd84"
uuid = "3bb67fe8-82b1-5028-8e26-92a6c54297fa"
version = "0.10.2"
weakdeps = ["Random", "Test"]

    [deps.TranscodingStreams.extensions]
    TestExt = ["Test", "Random"]

[[deps.Tricks]]
git-tree-sha1 = "eae1bb484cd63b36999ee58be2de6c178105112f"
uuid = "410a4b4d-49e4-4fbc-ab6d-cb71b17b3775"
version = "0.1.8"

[[deps.URIs]]
git-tree-sha1 = "67db6cc7b3821e19ebe75791a9dd19c9b1188f2b"
uuid = "5c2747f8-b7ea-4ff2-ba2e-563bfd36b1d4"
version = "1.5.1"

[[deps.UUIDs]]
deps = ["Random", "SHA"]
uuid = "cf7118a7-6976-5b1a-9a39-7adc72f591a4"

[[deps.Unicode]]
uuid = "4ec0a83e-493e-50e2-b9ac-8f72acf5a8f5"

[[deps.UnsafePointers]]
git-tree-sha1 = "c81331b3b2e60a982be57c046ec91f599ede674a"
uuid = "e17b2a0c-0bdf-430a-bd0c-3a23cae4ff39"
version = "1.0.0"

[[deps.Zlib_jll]]
deps = ["Libdl"]
uuid = "83775a58-1f1d-513f-b197-d71354ab007a"
version = "1.2.13+0"

[[deps.libblastrampoline_jll]]
deps = ["Artifacts", "Libdl"]
uuid = "8e850b90-86db-534c-a0d3-1478176c7d93"
version = "5.8.0+0"

[[deps.micromamba_jll]]
deps = ["Artifacts", "JLLWrappers", "LazyArtifacts", "Libdl"]
git-tree-sha1 = "66d07957bcf7e4930d933195aed484078dd8cbb5"
uuid = "f8abcde7-e9b7-5caa-b8af-a437887ae8e4"
version = "1.4.9+0"

[[deps.nghttp2_jll]]
deps = ["Artifacts", "Libdl"]
uuid = "8e850ede-7688-5339-a07c-302acd2aaf8d"
version = "1.52.0+1"

[[deps.p7zip_jll]]
deps = ["Artifacts", "Libdl"]
uuid = "3f19e933-33d8-53b3-aaab-bd5110c3b7a0"
version = "17.4.0+0"
"""

# ╔═╡ 00000000-0000-0000-0000-000000000003
PLUTO_CONDAPKG_TOML_CONTENTS = """
[deps]
matplotlib = ""
dill = ""

[pip.deps]
juliacall = ""
"""

# ╔═╡ Cell order:
# ╟─172fbef1-3f9e-4ca2-bdc5-8d2755d62c34
# ╟─16609b7c-0fa7-41d3-8dd4-4a99aaeeb0d7
# ╟─60a9e137-1f35-4268-ad10-be6104431e04
# ╟─35229634-2c40-4de9-8911-a61ceb32f663
# ╠═fa392c32-7ed6-11ee-02d6-e5f4f5490be6
# ╠═040b90c8-8ed3-4497-866a-bed69b2e27e1
# ╠═83f49510-e63b-45af-9c5e-0686f10d154f
# ╟─a421c2ba-f2b4-463a-bfb1-e05e5879e918
# ╠═6ffa64f4-0126-4536-912f-387d4ad9bbf5
# ╠═e4b67d9e-b974-470e-ab59-20f04117deb1
# ╠═7e148569-41e8-444f-a039-f5e91839bcfc
# ╟─ad6a5da9-304c-4d09-b59f-c35c31123b18
# ╟─07e65d43-6f09-4221-acfb-de05a64283e6
# ╠═ff1a1833-a060-4939-bf96-50d6bbc2b974
# ╟─d8f62255-a239-45bc-8042-0eda43caff8a
# ╠═97fcba32-bbca-4570-a4da-4a8438a5e10f
# ╠═5095d2c5-7b3c-4cb7-b694-d7ce4b32fd90
# ╟─c0afe0d1-3eb8-4274-b4cc-018097d1bdb2
# ╠═09f75fd2-6096-48d5-8f80-fd775e01025f
# ╟─34eb23e8-b0a6-4edc-911b-bedd8dd0a232
# ╠═149ee90f-d5ea-4791-8bad-3f3f260d9f28
# ╟─b6d0153c-e777-421f-8699-02340e0ad273
# ╠═da871125-8067-4441-b5df-d76d609bc46d
# ╟─10246e4d-66e3-41fb-b92c-4900e0d5454b
# ╠═5f277b91-20ef-448c-83f8-3ee504644f3b
# ╟─e232f3f9-9687-4b1a-9428-47f9aef9ec6b
# ╟─6a1f8649-eb6b-47b5-bae2-b834f7f79f69
# ╠═0316b6ed-5fa7-41e1-8230-616150c3b2a0
# ╟─7d670f9f-6fd5-40fa-ac82-4a6b034a2b7c
# ╠═bc23101c-fdee-4fa8-a2e0-105d73eeefb5
# ╠═36679b5b-5fcc-499b-bd0e-74556d34daf3
# ╟─00000000-0000-0000-0000-000000000001
# ╟─00000000-0000-0000-0000-000000000002
# ╟─00000000-0000-0000-0000-000000000003
