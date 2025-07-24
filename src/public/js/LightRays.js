// WebGL Light Rays implementation based on lightrays.txt
class LightRays {
    constructor(container, options = {}) {
        this.container = container;
        this.options = {
            raysOrigin: options.raysOrigin || "top-center",
            raysColor: options.raysColor || "#ffd700",
            raysSpeed: options.raysSpeed || 1,
            lightSpread: options.lightSpread || 0.5,
            rayLength: options.rayLength || 3,
            pulsating: options.pulsating || false,
            fadeDistance: options.fadeDistance || 1,
            saturation: options.saturation || 1,
            followMouse: options.followMouse || false,
            mouseInfluence: options.mouseInfluence || 0.1,
            noiseAmount: options.noiseAmount || 0,
            distortion: options.distortion || 0,
            ...options
        };

        this.mouse = { x: 0.5, y: 0.5 };
        this.smoothMouse = { x: 0.5, y: 0.5 };
        this.animationId = null;
        this.isVisible = false;

        this.init();
    }

    hexToRgb(hex) {
        const m = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
        return m ? [
            parseInt(m[1], 16) / 255,
            parseInt(m[2], 16) / 255,
            parseInt(m[3], 16) / 255,
        ] : [1, 1, 1];
    }

    getAnchorAndDir(origin, w, h) {
        const outside = 0.2;
        switch (origin) {
            case "top-left":
                return { anchor: [0, -outside * h], dir: [0, 1] };
            case "top-right":
                return { anchor: [w, -outside * h], dir: [0, 1] };
            case "left":
                return { anchor: [-outside * w, 0.5 * h], dir: [1, 0] };
            case "right":
                return { anchor: [(1 + outside) * w, 0.5 * h], dir: [-1, 0] };
            case "bottom-left":
                return { anchor: [0, (1 + outside) * h], dir: [0, -1] };
            case "bottom-center":
                return { anchor: [0.5 * w, (1 + outside) * h], dir: [0, -1] };
            case "bottom-right":
                return { anchor: [w, (1 + outside) * h], dir: [0, -1] };
            default: // "top-center"
                return { anchor: [0.5 * w, -outside * h], dir: [0, 1] };
        }
    }

    init() {
        // Setup intersection observer
        this.observer = new IntersectionObserver((entries) => {
            const entry = entries[0];
            this.isVisible = entry.isIntersecting;
            if (this.isVisible) {
                this.initWebGL();
            } else {
                this.cleanup();
            }
        }, { threshold: 0.1 });

        this.observer.observe(this.container);

        // Mouse tracking
        if (this.options.followMouse) {
            this.handleMouseMove = (e) => {
                const rect = this.container.getBoundingClientRect();
                const x = (e.clientX - rect.left) / rect.width;
                const y = (e.clientY - rect.top) / rect.height;
                this.mouse = { x, y };
            };
            window.addEventListener("mousemove", this.handleMouseMove);
        }
    }

    initWebGL() {
        if (!this.isVisible || this.canvas) return;

        // Create canvas
        this.canvas = document.createElement('canvas');
        this.canvas.style.width = '100%';
        this.canvas.style.height = '100%';
        this.canvas.style.position = 'absolute';
        this.canvas.style.top = '0';
        this.canvas.style.left = '0';
        this.canvas.style.pointerEvents = 'none';
        this.canvas.style.zIndex = '1';

        this.container.appendChild(this.canvas);

        // Get WebGL context
        this.gl = this.canvas.getContext('webgl') || this.canvas.getContext('experimental-webgl');
        if (!this.gl) {
            console.warn('WebGL not supported, falling back to CSS');
            return;
        }

        this.setupShaders();
        this.setupGeometry();
        this.updateSize();
        this.startAnimation();

        // Handle resize
        this.resizeHandler = () => this.updateSize();
        window.addEventListener('resize', this.resizeHandler);
    }

    setupShaders() {
        const vertexShaderSource = `
            attribute vec2 position;
            varying vec2 vUv;
            void main() {
                vUv = position * 0.5 + 0.5;
                gl_Position = vec4(position, 0.0, 1.0);
            }
        `;

        const fragmentShaderSource = `
            precision highp float;

            uniform float iTime;
            uniform vec2 iResolution;
            uniform vec2 rayPos;
            uniform vec2 rayDir;
            uniform vec3 raysColor;
            uniform float raysSpeed;
            uniform float lightSpread;
            uniform float rayLength;
            uniform float pulsating;
            uniform float fadeDistance;
            uniform float saturation;
            uniform vec2 mousePos;
            uniform float mouseInfluence;
            uniform float noiseAmount;
            uniform float distortion;

            varying vec2 vUv;

            float noise(vec2 st) {
                return fract(sin(dot(st.xy, vec2(12.9898,78.233))) * 43758.5453123);
            }

            float rayStrength(vec2 raySource, vec2 rayRefDirection, vec2 coord, float seedA, float seedB, float speed) {
                vec2 sourceToCoord = coord - raySource;
                vec2 dirNorm = normalize(sourceToCoord);
                float cosAngle = dot(dirNorm, rayRefDirection);

                float distortedAngle = cosAngle + distortion * sin(iTime * 2.0 + length(sourceToCoord) * 0.01) * 0.2;
                
                float spreadFactor = pow(max(distortedAngle, 0.0), 1.0 / max(lightSpread, 0.001));

                float distance = length(sourceToCoord);
                float maxDistance = iResolution.x * rayLength;
                float lengthFalloff = clamp((maxDistance - distance) / maxDistance, 0.0, 1.0);
                
                float fadeFalloff = clamp((iResolution.x * fadeDistance - distance) / (iResolution.x * fadeDistance), 0.5, 1.0);
                float pulse = pulsating > 0.5 ? (0.8 + 0.2 * sin(iTime * speed * 3.0)) : 1.0;

                float baseStrength = clamp(
                    (0.45 + 0.15 * sin(distortedAngle * seedA + iTime * speed)) +
                    (0.3 + 0.2 * cos(-distortedAngle * seedB + iTime * speed)),
                    0.0, 1.0
                );

                return baseStrength * lengthFalloff * fadeFalloff * spreadFactor * pulse;
            }

            void main() {
                vec2 coord = vec2(gl_FragCoord.x, iResolution.y - gl_FragCoord.y);
                
                vec2 finalRayDir = rayDir;
                if (mouseInfluence > 0.0) {
                    vec2 mouseScreenPos = mousePos * iResolution.xy;
                    vec2 mouseDirection = normalize(mouseScreenPos - rayPos);
                    finalRayDir = normalize(mix(rayDir, mouseDirection, mouseInfluence));
                }

                vec4 rays1 = vec4(1.0) * rayStrength(rayPos, finalRayDir, coord, 36.2214, 21.11349, 1.5 * raysSpeed);
                vec4 rays2 = vec4(1.0) * rayStrength(rayPos, finalRayDir, coord, 22.3991, 18.0234, 1.1 * raysSpeed);

                vec4 fragColor = rays1 * 0.5 + rays2 * 0.4;

                if (noiseAmount > 0.0) {
                    float n = noise(coord * 0.01 + iTime * 0.1);
                    fragColor.rgb *= (1.0 - noiseAmount + noiseAmount * n);
                }

                float brightness = 1.0 - (coord.y / iResolution.y);
                fragColor.x *= 0.1 + brightness * 0.8;
                fragColor.y *= 0.3 + brightness * 0.6;
                fragColor.z *= 0.5 + brightness * 0.5;

                if (saturation != 1.0) {
                    float gray = dot(fragColor.rgb, vec3(0.299, 0.587, 0.114));
                    fragColor.rgb = mix(vec3(gray), fragColor.rgb, saturation);
                }

                fragColor.rgb *= raysColor;
                gl_FragColor = fragColor;
            }
        `;

        // Create and compile shaders
        this.vertexShader = this.createShader(this.gl.VERTEX_SHADER, vertexShaderSource);
        this.fragmentShader = this.createShader(this.gl.FRAGMENT_SHADER, fragmentShaderSource);

        // Create program
        this.program = this.gl.createProgram();
        this.gl.attachShader(this.program, this.vertexShader);
        this.gl.attachShader(this.program, this.fragmentShader);
        this.gl.linkProgram(this.program);

        if (!this.gl.getProgramParameter(this.program, this.gl.LINK_STATUS)) {
            console.error('Program linking failed:', this.gl.getProgramInfoLog(this.program));
            return;
        }

        this.gl.useProgram(this.program);

        // Get uniform locations
        this.uniforms = {
            iTime: this.gl.getUniformLocation(this.program, 'iTime'),
            iResolution: this.gl.getUniformLocation(this.program, 'iResolution'),
            rayPos: this.gl.getUniformLocation(this.program, 'rayPos'),
            rayDir: this.gl.getUniformLocation(this.program, 'rayDir'),
            raysColor: this.gl.getUniformLocation(this.program, 'raysColor'),
            raysSpeed: this.gl.getUniformLocation(this.program, 'raysSpeed'),
            lightSpread: this.gl.getUniformLocation(this.program, 'lightSpread'),
            rayLength: this.gl.getUniformLocation(this.program, 'rayLength'),
            pulsating: this.gl.getUniformLocation(this.program, 'pulsating'),
            fadeDistance: this.gl.getUniformLocation(this.program, 'fadeDistance'),
            saturation: this.gl.getUniformLocation(this.program, 'saturation'),
            mousePos: this.gl.getUniformLocation(this.program, 'mousePos'),
            mouseInfluence: this.gl.getUniformLocation(this.program, 'mouseInfluence'),
            noiseAmount: this.gl.getUniformLocation(this.program, 'noiseAmount'),
            distortion: this.gl.getUniformLocation(this.program, 'distortion')
        };

        // Set initial uniform values
        const color = this.hexToRgb(this.options.raysColor);
        this.gl.uniform3f(this.uniforms.raysColor, color[0], color[1], color[2]);
        this.gl.uniform1f(this.uniforms.raysSpeed, this.options.raysSpeed);
        this.gl.uniform1f(this.uniforms.lightSpread, this.options.lightSpread);
        this.gl.uniform1f(this.uniforms.rayLength, this.options.rayLength);
        this.gl.uniform1f(this.uniforms.pulsating, this.options.pulsating ? 1.0 : 0.0);
        this.gl.uniform1f(this.uniforms.fadeDistance, this.options.fadeDistance);
        this.gl.uniform1f(this.uniforms.saturation, this.options.saturation);
        this.gl.uniform1f(this.uniforms.mouseInfluence, this.options.mouseInfluence);
        this.gl.uniform1f(this.uniforms.noiseAmount, this.options.noiseAmount);
        this.gl.uniform1f(this.uniforms.distortion, this.options.distortion);
        this.gl.uniform2f(this.uniforms.mousePos, 0.5, 0.5);
    }

    createShader(type, source) {
        const shader = this.gl.createShader(type);
        this.gl.shaderSource(shader, source);
        this.gl.compileShader(shader);

        if (!this.gl.getShaderParameter(shader, this.gl.COMPILE_STATUS)) {
            console.error('Shader compilation failed:', this.gl.getShaderInfoLog(shader));
            this.gl.deleteShader(shader);
            return null;
        }

        return shader;
    }

    setupGeometry() {
        // Create a full-screen triangle
        const vertices = new Float32Array([
            -1, -1,
             3, -1,
            -1,  3
        ]);

        this.vertexBuffer = this.gl.createBuffer();
        this.gl.bindBuffer(this.gl.ARRAY_BUFFER, this.vertexBuffer);
        this.gl.bufferData(this.gl.ARRAY_BUFFER, vertices, this.gl.STATIC_DRAW);

        const positionLocation = this.gl.getAttribLocation(this.program, 'position');
        this.gl.enableVertexAttribArray(positionLocation);
        this.gl.vertexAttribPointer(positionLocation, 2, this.gl.FLOAT, false, 0, 0);
    }

    updateSize() {
        if (!this.canvas || !this.gl) return;

        const rect = this.container.getBoundingClientRect();
        const dpr = Math.min(window.devicePixelRatio, 2);

        this.canvas.width = rect.width * dpr;
        this.canvas.height = rect.height * dpr;

        this.gl.viewport(0, 0, this.canvas.width, this.canvas.height);
        this.gl.uniform2f(this.uniforms.iResolution, this.canvas.width, this.canvas.height);

        // Update ray position and direction
        const { anchor, dir } = this.getAnchorAndDir(
            this.options.raysOrigin,
            this.canvas.width,
            this.canvas.height
        );
        this.gl.uniform2f(this.uniforms.rayPos, anchor[0], anchor[1]);
        this.gl.uniform2f(this.uniforms.rayDir, dir[0], dir[1]);
    }

    startAnimation() {
        const animate = (time) => {
            if (!this.gl || !this.isVisible) return;

            this.gl.uniform1f(this.uniforms.iTime, time * 0.001);

            // Update mouse position with smoothing
            if (this.options.followMouse && this.options.mouseInfluence > 0.0) {
                const smoothing = 0.92;
                this.smoothMouse.x = this.smoothMouse.x * smoothing + this.mouse.x * (1 - smoothing);
                this.smoothMouse.y = this.smoothMouse.y * smoothing + this.mouse.y * (1 - smoothing);
                this.gl.uniform2f(this.uniforms.mousePos, this.smoothMouse.x, this.smoothMouse.y);
            }

            // Clear and render
            this.gl.clearColor(0, 0, 0, 0);
            this.gl.clear(this.gl.COLOR_BUFFER_BIT);
            this.gl.drawArrays(this.gl.TRIANGLES, 0, 3);

            this.animationId = requestAnimationFrame(animate);
        };

        this.animationId = requestAnimationFrame(animate);
    }

    cleanup() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
            this.animationId = null;
        }

        if (this.resizeHandler) {
            window.removeEventListener('resize', this.resizeHandler);
            this.resizeHandler = null;
        }

        if (this.canvas && this.canvas.parentNode) {
            this.canvas.parentNode.removeChild(this.canvas);
            this.canvas = null;
        }

        if (this.gl) {
            // Clean up WebGL resources
            if (this.program) {
                this.gl.deleteProgram(this.program);
                this.program = null;
            }
            if (this.vertexShader) {
                this.gl.deleteShader(this.vertexShader);
                this.vertexShader = null;
            }
            if (this.fragmentShader) {
                this.gl.deleteShader(this.fragmentShader);
                this.fragmentShader = null;
            }
            if (this.vertexBuffer) {
                this.gl.deleteBuffer(this.vertexBuffer);
                this.vertexBuffer = null;
            }

            // Lose WebGL context
            const loseContextExt = this.gl.getExtension('WEBGL_lose_context');
            if (loseContextExt) {
                loseContextExt.loseContext();
            }
            this.gl = null;
        }
    }

    destroy() {
        this.cleanup();

        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }

        if (this.handleMouseMove) {
            window.removeEventListener('mousemove', this.handleMouseMove);
            this.handleMouseMove = null;
        }
    }
}

// Export for use
window.LightRays = LightRays;
